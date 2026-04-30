from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.triage import classify_triage
from services.knowledge import build_legal_guidance, format_response_text

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Project Aji"}


@router.post("/triage")
async def test_triage(body: dict):
    """
    Test triage logic without going through WhatsApp.
    POST { "transcript": "bank nahi help karucha, please help" }
    """
    transcript = body.get("transcript", "")
    triage = classify_triage(transcript)
    return triage.model_dump()


@router.post("/guidance")
async def test_guidance(body: dict):
    """
    Test full pipeline: triage → guidance → formatted text.
    POST { "transcript": "bank refuse karila, mrutyu praman achi" }
    """
    transcript = body.get("transcript", "")
    triage = classify_triage(transcript)
    guidance = build_legal_guidance(triage)
    text = format_response_text(guidance, distress_high=True)
    return {
        "triage": triage.model_dump(),
        "guidance": guidance.model_dump(),
        "response_text": text,
    }
