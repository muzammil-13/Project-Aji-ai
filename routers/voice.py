import os
import httpx

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse

from models.schemas import IncomingVoiceMessage, AjiResponse, DistressLevel
from services.sarvam import transcribe_audio, synthesize_speech
from services.triage import classify_triage, get_next_guided_question
from services.knowledge import build_legal_guidance, format_response_text

router = APIRouter(prefix="/voice", tags=["voice"])

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0"

async def send_whatsapp_text(phone: str, text: str):
    """
    Sends a real WhatsApp text message via Meta Graph API.
    """
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    token = os.getenv("WHATSAPP_TOKEN")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{WHATSAPP_API_URL}/{phone_number_id}/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": text},
            },
            timeout=10.0,
        )
        if response.status_code != 200:
            print(f"[ERROR] WhatsApp send failed: {response.text}")
        else:
            print(f"[OK] Message sent to {phone}")


async def send_whatsapp_audio(phone: str, audio_bytes: bytes, fallback_text: str):
    """
    V1: sends text fallback since audio upload needs extra setup.
    V2: upload audio_bytes to Meta media API first, then send audio message.
    """
    await send_whatsapp_text(phone, fallback_text)

# Add this GET endpoint — Meta calls it once to verify your webhook is real

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Meta sends a GET request with these query params to verify your webhook.
    You must echo back hub.challenge if your verify token matches.
    """
    import os
    mode      = request.query_params.get("hub.mode")
    token     = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        return PlainTextResponse(content=challenge)

    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Entry point for all incoming WhatsApp messages.
    WhatsApp Business API sends a POST here when a user sends a message.

    V1: processes synchronously, returns 200 fast, processes in background.
    TODO V2: add message queue (Celery/Redis) for scale.
    """
    payload = await request.json()

    # WhatsApp wraps messages in a nested structure
    try:
        message_data = payload["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError):
        # Could be a status update, not a message — ignore silently
        return JSONResponse({"status": "ignored"}, status_code=200)

    # Only handle audio messages for now
    if message_data.get("type") != "audio":
        return JSONResponse(
            {"status": "unsupported_type", "detail": "Only voice messages supported in V1"},
            status_code=200,  # return 200 so WhatsApp doesn't retry
        )

    incoming = IncomingVoiceMessage(
        sender_phone=message_data["from"],
        audio_url=message_data["audio"]["id"],  # media ID, not a direct URL
        message_id=message_data["id"],
        timestamp=message_data["timestamp"],
    )

    background_tasks.add_task(process_voice_message, incoming)

    # Respond immediately — WhatsApp requires a fast 200
    return JSONResponse({"status": "received"}, status_code=200)


async def process_voice_message(incoming: IncomingVoiceMessage):
    """
    Full pipeline: audio → transcript → triage → guidance → audio response.
    Runs in background so the webhook returns fast.
    """
    try:
        # Step 1: transcribe
        stt_result = await transcribe_audio(incoming.audio_url)
        transcript = stt_result["transcript"]
        language = stt_result["language_code"]

        # Step 2: triage
        triage = classify_triage(transcript)

        # Step 3: decide response
        next_question = get_next_guided_question(triage)

        if next_question:
            # Still in guided mode, ask next question
            response_text = next_question
        else:
            # All context gathered — build legal guidance
            guidance = build_legal_guidance(triage)
            response_text = format_response_text(
                guidance,
                distress_high=(triage.distress_level == DistressLevel.HIGH),
            )

        # Step 4: synthesize to audio
        audio_bytes = await synthesize_speech(response_text, language_code=language)

        # Step 5: send back via WhatsApp
        # TODO: upload audio_bytes to WhatsApp media API, then send media message
        # Placeholder — wire up send_whatsapp_audio() when you have WA Business API creds
        await send_whatsapp_audio(incoming.sender_phone, audio_bytes, response_text)

    except Exception as e:
        # Log and fail gracefully — never leave a user without a response
        print(f"[ERROR] Failed to process message from {incoming.sender_phone}: {e}")
        await send_whatsapp_text(
            incoming.sender_phone,
            "Mafi karanti. Kichhi samasyā achhi. Kuchha samaya pachhe punah try karanti."
            # "Sorry, there was a problem. Please try again in a moment."
        )


async def send_whatsapp_audio(phone: str, audio_bytes: bytes, fallback_text: str):
    """
    TODO: implement WhatsApp Business API media upload + send.
    For now, sends text fallback.
    """
    print(f"[STUB] Would send audio to {phone}. Fallback text: {fallback_text[:80]}...")
    await send_whatsapp_text(phone, fallback_text)


async def send_whatsapp_text(phone: str, text: str):
    """
    TODO: implement WhatsApp Business API text send.
    """
    print(f"[STUB] Would send text to {phone}: {text[:80]}...")
