The **Vibe-Code Architecture** for Project Aji is designed to be a "Zero-Trust, High-Empathy" bridge. It treats the bank’s secure infrastructure as the **source of truth** and Sarvam AI’s 2026 Sovereign Stack as the **human interface**.

Since we are prioritizing **UX and safety**, the architecture follows a "Decoupled" approach: the AI handles the conversation, but never the sensitive banking credentials.

---

### 1. The Multi-Layered Architecture

The system is organized into three distinct zones to ensure that no critical data is leaked while providing a seamless native experience.



#### **Zone A: The Bank Vault (Secure Environment)**
* **Token Generator:** A micro-service inside the bank's existing app.
* **Scoped API:** A restricted endpoint that only confirms if a `Token` is valid and returns the `Customer_Language_Preference` and `Service_Type` (e.g., "Verification"). No balance or transaction data is exposed.

#### **Zone B: The Aji Empathy Bridge (Middleware)**
* **The Orchestrator (FastAPI):** Manages the flow between WhatsApp and the AI.
* **The Logic Gate:** Validates the 6-digit token before allowing the AI to access the user's banking context.

#### **Zone C: The Sovereign AI Layer (Sarvam AI 2026)**
* **Sarvam Saaras v3 (STT):** The "Ears." Specifically tuned for the emotional, high-stress speech of rural users.
* **Sarvam-M (Hybrid LLM):** The "Brain." It operates under a "Public Good" system prompt that forbids financial discussions.
* **Sarvam Bulbul v3 (TTS):** The "Voice." Generates the warm "Roopa" voice response in native Odia.

---

### 2. The Interaction Logic Flow

Here is how the data moves through the system during a session:

| Component | Input | Action | Output |
| :--- | :--- | :--- | :--- |
| **WhatsApp Hook** | Voice Note / Text | Receives the user's raw message. | Encrypted Payload |
| **Identity Check** | 6-Digit Token | Matches token against Bank API. | `Verified: True` |
| **Sentiment Analysis** | Audio Stream | Detects distress levels (via Saaras v3). | `Stress_Level: High` |
| **Logic Engine** | User Intent | Finds the right legal/banking clause. | Empathetic Advice |
| **Voice Synthesis** | Response Text | Converts text to a 24kHz Odia voice note. | `.wav` Voice Note |

---

### 3. Vibe-Code Technical Moat (Safety Features)

To keep this "Public Good" safe, we implement **Sovereign Guardrails**:

* **PII Scrubbing:** Before the transcript is sent to the LLM, a local regex filter scrubs any mentions of phone numbers, Aadhaar numbers, or card details.
* **Session-Only Memory:** Aji "forgets" the specific conversation details the moment the session expires. Only the "Outcome" (e.g., "User informed of rights") is logged for the bank.
* **Latency Budget:** By using Sarvam’s 2026 edge-optimized models, the entire round-trip (Voice in -> Voice out) stays under **1.2 seconds**, ensuring the user doesn't feel like they are talking to a slow machine.

---

### 4. Why this Architecture works for Public Good:
1.  **Low Friction:** It uses WhatsApp, which requires zero new learning for the user.
2.  **Native Support:** It doesn't translate Odia to English to "think"—it thinks in Odia natively using Sarvam-M.
3.  **Scalability:** Because it's a middleware, SBI, PNB, or any regional Gramya bank can plug their API into the same "Aji" bridge.

---

### The Prototype Blueprint
Since we are focused on UX, the architecture is designed to be **"Stateless."** This means if the user's phone dies and they come back an hour later, they simply generate a new token and Aji picks up exactly where she left off based on the last saved "State" in the bank's secure log.
