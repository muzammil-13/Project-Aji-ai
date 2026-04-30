# services/triage.py
# PURPOSE: Pure logic. No HTTP. No FastAPI. Just: transcript → TriageResult.

from models.schemas import TriageResult, UserMode, DistressLevel, BankCooperation


HIGH_DISTRESS_SIGNALS = [
    "mara", "mariba", "death", "died", "gone", "passed",
    "morila", "muruchi", "help", "please", "urgent",
    "crying", "kanduchi", "kana kariba",
]

BANK_REFUSAL_SIGNALS = [
    "refuse", "not helping", "nahi", "deilanhi", "denied",
    "send away", "pathei dila", "boluchi nahi",
]

DOCUMENT_SIGNALS = {
    "death_cert": ["death certificate", "mrutyu praman", "mrityu"],
    "id_proof": ["aadhaar", "aadhar", "id card", "voter id"],
    "heir_cert": ["legal heir", "varis praman", "succession"],
}


def classify_triage(transcript: str) -> TriageResult:
    """
    Rule-based triage for V1.
    Upgrade to Sarvam-M LLM call in V2 when you have training examples.
    """
    text = transcript.lower()

    high_signals_found = sum(1 for kw in HIGH_DISTRESS_SIGNALS if kw in text)

    if high_signals_found >= 2:
        distress_level = DistressLevel.HIGH
    elif high_signals_found == 1:
        distress_level = DistressLevel.MEDIUM
    else:
        distress_level = DistressLevel.LOW

    direct_question_signals = ["what", "how", "where", "when", "kana", "kemiti", "kahim"]
    is_direct = "?" in text or any(q in text for q in direct_question_signals)

    if distress_level == DistressLevel.HIGH:
        mode = UserMode.GUIDED
    elif is_direct and distress_level == DistressLevel.LOW:
        mode = UserMode.DIRECT
    else:
        mode = UserMode.GUIDED

    bank_cooperation = BankCooperation.UNKNOWN
    if any(kw in text for kw in BANK_REFUSAL_SIGNALS):
        bank_cooperation = BankCooperation.REFUSING

    docs_mentioned = any(
        any(kw in text for kw in kws)
        for kws in DOCUMENT_SIGNALS.values()
    )

    return TriageResult(
        mode=mode,
        distress_level=distress_level,
        bank_cooperation=bank_cooperation,
        documents_ready=docs_mentioned if docs_mentioned else None,
        direct_query=transcript if mode == UserMode.DIRECT else None,
    )


def get_next_guided_question(triage: TriageResult) -> str:
    """
    Returns the next unanswered question Aji should ask.
    Returns None when all 5 questions are answered → proceed to resolution.
    """
    if triage.relation_to_deceased is None:
        return "Aapana paribara re kana hoi gala? (Who passed away in your family?)"

    if triage.bank_name is None:
        return "Sei bank ra naam kana? (What is the name of the bank?)"

    if triage.documents_ready is None:
        return (
            "Aapana pasa mrutyu praman patra, id card, ebam legal heir certificate achi ki? "
            "(Do you have the death certificate, ID, and legal heir certificate?)"
        )

    if triage.bank_cooperation == BankCooperation.UNKNOWN:
        return (
            "Bank aapananka sahajya karuchi ki? "
            "(Is the bank cooperating with you?)"
        )

    if triage.district is None:
        return "Aapana kahim rahuchi? Kaunsi district? (Where are you? Which district?)"

    return None