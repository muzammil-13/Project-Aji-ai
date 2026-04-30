from enum import Enum
from pydantic import BaseModel
from typing import Optional


# --- Enums ---

class UserMode(str, Enum):
    GUIDED = "guided"       # distressed, Aji leads
    DIRECT = "direct"       # calm, user has a specific question


class DistressLevel(str, Enum):
    HIGH = "high"           # grief, crying, urgent
    MEDIUM = "medium"       # worried, confused
    LOW = "low"             # calm, informational


class BankCooperation(str, Enum):
    REFUSING = "refusing"   # bank actively blocking
    SLOW = "slow"           # cooperating but delayed
    UNKNOWN = "unknown"     # not yet established


# --- Incoming from WhatsApp webhook ---

class IncomingVoiceMessage(BaseModel):
    sender_phone: str
    audio_url: str          # WhatsApp media URL
    message_id: str
    timestamp: int


# --- After STT ---

class TranscribedMessage(BaseModel):
    sender_phone: str
    message_id: str
    transcript: str
    detected_language: str  # e.g. "or" (Odia), "en"


# --- After triage ---

class TriageResult(BaseModel):
    mode: UserMode
    distress_level: DistressLevel
    # Guided mode: tracks which questions are answered
    relation_to_deceased: Optional[str] = None     # Q1
    bank_name: Optional[str] = None                # Q2
    documents_ready: Optional[bool] = None         # Q3
    bank_cooperation: BankCooperation = BankCooperation.UNKNOWN  # Q4
    district: Optional[str] = None                 # Q5
    # Direct mode: the extracted question
    direct_query: Optional[str] = None


# --- Legal knowledge response ---

class LegalGuidance(BaseModel):
    rights_explanation: str     # what the citizen is entitled to
    next_steps: list[str]       # ordered action items
    escalation_path: Optional[str] = None   # ombudsman / DLSA if needed
    relevant_law: Optional[str] = None      # e.g. "RBI Circular 2023"


# --- Final response to send back ---

class AjiResponse(BaseModel):
    recipient_phone: str
    text_response: str          # text version (for logging)
    audio_url: Optional[str] = None  # TTS output URL from Sarvam
    follow_up_prompt: Optional[str] = None  # next question Aji will ask
