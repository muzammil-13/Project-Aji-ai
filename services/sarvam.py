import httpx
import os
from pathlib import Path


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_BASE_URL = "https://api.sarvam.ai"

# Model names from Sarvam 2026 lineup
STT_MODEL = "saaras:v3"
TTS_MODEL = "bulbul:v3"
TTS_VOICE = "Roopa"         # warm, human voice per the project spec


async def transcribe_audio(audio_url: str) -> dict:
    """
    Download audio from WhatsApp URL, send to Sarvam STT.
    Returns: { transcript: str, language_code: str }
    """
    # Step 1: download the audio bytes from WhatsApp
    async with httpx.AsyncClient() as client:
        audio_response = await client.get(audio_url)
        audio_response.raise_for_status()
        audio_bytes = audio_response.content

    # Step 2: send to Sarvam STT
    async with httpx.AsyncClient() as client:
        stt_response = await client.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers={"api-subscription-key": SARVAM_API_KEY},
            files={"file": ("audio.ogg", audio_bytes, "audio/ogg")},
            data={
                "model": STT_MODEL,
                "language_code": "or-IN",   # Odia; Sarvam handles code-mixing
                "with_timestamps": False,
            },
            timeout=30.0,
        )
        stt_response.raise_for_status()
        result = stt_response.json()

    return {
        "transcript": result.get("transcript", ""),
        "language_code": result.get("language_code", "or-IN"),
    }


async def synthesize_speech(text: str, language_code: str = "or-IN") -> bytes:
    """
    Convert text response to Odia audio via Sarvam TTS.
    Returns raw audio bytes (wav).
    """
    async with httpx.AsyncClient() as client:
        tts_response = await client.post(
            f"{SARVAM_BASE_URL}/text-to-speech",
            headers={
                "api-subscription-key": SARVAM_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "inputs": [text],
                "target_language_code": language_code,
                "speaker": TTS_VOICE,
                "model": TTS_MODEL,
                "enable_preprocessing": True,
            },
            timeout=30.0,
        )
        tts_response.raise_for_status()
        result = tts_response.json()

    # Sarvam returns base64-encoded audio
    import base64
    audio_b64 = result["audios"][0]
    return base64.b64decode(audio_b64)
