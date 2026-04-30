from models.schemas import TriageResult, LegalGuidance, BankCooperation


# V1: hardcoded legal content derived from RBI Master Circular on deceased depositors
# Source: RBI/2023-24/53 — Master Circular on Customer Service
# TODO: replace with DB lookup / vector search in V2

LEGAL_CONTENT = {
    "doorstep_banking": {
        "rights": (
            "RBI guidelines mandate that banks must offer Doorstep Banking services. "
            "You do not need to visit the branch physically. The bank is required to send "
            "an officer to your home to complete the verification process."
        ),
        "steps": [
            "Call the bank's toll-free number and request Doorstep Banking for deceased depositor settlement.",
            "If they refuse, ask to speak with the Branch Manager directly.",
            "Mention RBI Master Circular on Customer Service (2023-24) — banks are legally bound by this.",
            "Keep a written record (SMS/email) of every interaction with the bank.",
        ],
        "law": "RBI Master Circular - Customer Service in Banks (2023-24)",
    },
    "ombudsman": {
        "rights": (
            "If the bank refuses to cooperate, you can file a complaint with the RBI Banking Ombudsman. "
            "This is free of charge. The bank must respond within 30 days of your complaint. "
            "The Ombudsman can order the bank to compensate you."
        ),
        "steps": [
            "File a complaint at: https://cms.rbi.org.in (online portal, free).",
            "Or call RBI toll-free: 14448.",
            "You need: bank name, branch, account number of deceased, your relation, dates of bank refusal.",
            "The bank has 30 days to resolve after your complaint is registered.",
        ],
        "escalation": "RBI Banking Ombudsman — cms.rbi.org.in or call 14448",
        "law": "Banking Ombudsman Scheme 2006 (amended 2017)",
    },
    "required_documents": {
        "rights": (
            "To claim a deceased person's bank account, you need three core documents. "
            "No other documents can be demanded by the bank beyond these."
        ),
        "steps": [
            "Death Certificate — issued by Municipal Corporation or Gram Panchayat.",
            "Legal Heir Certificate — issued by Tehsildar / SDM office of your district.",
            "Your identity proof (Aadhaar card is sufficient).",
            "If the account has a nominee, the process is simpler — nominee just needs death cert + their ID.",
        ],
        "law": "RBI Circular on Settlement of Claims of Deceased Depositors",
    },
}


def build_legal_guidance(triage: TriageResult) -> LegalGuidance:
    """
    Selects the right legal content based on triage state.
    V1: rule-based selection. V2: semantic search over a full legal KB.
    """

    # Case 1: Bank is actively refusing — lead with ombudsman rights
    if triage.bank_cooperation == BankCooperation.REFUSING:
        content = LEGAL_CONTENT["ombudsman"]
        return LegalGuidance(
            rights_explanation=content["rights"],
            next_steps=content["steps"],
            escalation_path=content["escalation"],
            relevant_law=content["law"],
        )

    # Case 2: Documents question — user doesn't have docs ready
    if triage.documents_ready is False:
        content = LEGAL_CONTENT["required_documents"]
        return LegalGuidance(
            rights_explanation=content["rights"],
            next_steps=content["steps"],
            relevant_law=content["law"],
        )

    # Case 3: Default — explain doorstep banking first
    content = LEGAL_CONTENT["doorstep_banking"]
    return LegalGuidance(
        rights_explanation=content["rights"],
        next_steps=content["steps"],
        relevant_law=content["law"],
    )


def format_response_text(guidance: LegalGuidance, distress_high: bool = False) -> str:
    """
    Formats the legal guidance into a warm, plain-language response.
    High distress = shorter, simpler, more empathetic opening.
    """
    if distress_high:
        opening = "Aapana ekla nahin. Aji aapananka sahajya karibe. "
        # "You are not alone. Aji will help you."
    else:
        opening = ""

    steps_text = " ".join(
        f"{i+1}. {step}" for i, step in enumerate(guidance.next_steps)
    )

    escalation_text = ""
    if guidance.escalation_path:
        escalation_text = f" Jadi bank nahi mane, aapana RBI te complaint kariba parin: {guidance.escalation_path}."

    return (
        f"{opening}"
        f"{guidance.rights_explanation} "
        f"{steps_text}"
        f"{escalation_text}"
    )
