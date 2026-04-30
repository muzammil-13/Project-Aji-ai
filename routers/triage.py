# routers/triage.py
# PURPOSE: HTTP only. Receives request, calls services/triage.py, returns response.
#          No business logic lives here.

from fastapi import APIRouter
from pydantic import BaseModel
from services.triage import classify_triage, get_next_guided_question

router = APIRouter(prefix="/triage", tags=["triage"])


class TriageRequest(BaseModel):
    transcript: str


@router.post("/classify")
async def classify(body: TriageRequest):
    """
    Test triage classification directly.
    POST { "transcript": "bank nahi help karucha, please help" }
    """
    result = classify_triage(body.transcript)
    return result.model_dump()


@router.post("/next-question")
async def next_question(body: dict):
    """
    Given a partial TriageResult, returns what Aji should ask next.
    Useful for testing guided mode step by step.

    POST {
        "transcript": "bank nahi help karucha",
        "relation_to_deceased": "mother",
        "bank_name": null
    }
    """
    from models.schemas import TriageResult, BankCooperation
    triage = classify_triage(body.get("transcript", ""))

    # Override with any fields the caller already knows
    triage.relation_to_deceased = body.get("relation_to_deceased")
    triage.bank_name = body.get("bank_name")
    triage.documents_ready = body.get("documents_ready")
    triage.district = body.get("district")

    question = get_next_guided_question(triage)
    return {
        "next_question": question,
        "all_answered": question is None,
    }