Simple. Three steps.

---

**Step 1: Create your `.env` file**

```bash
cd project-aji
cp .env.example .env
```

For local testing you don't need real keys yet — the Sarvam and WhatsApp calls are stubbed. Leave the `.env` as-is.

---

**Step 2: Install dependencies and run**

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

**Step 3: Test the endpoints**

Open a second terminal. Use `curl` or just open your browser.

**Health check (browser works):**

```
http://localhost:8000/debug/health
```

**Test triage (curl):**

```bash
curl -X POST http://localhost:8000/triage/classify \
  -H "Content-Type: application/json" \
  -d '{"transcript": "bank nahi help karucha, please help, mara"}'
```

**Test full pipeline — triage + guidance + response text:**

```bash
curl -X POST http://localhost:8000/debug/guidance \
  -H "Content-Type: application/json" \
  -d '{"transcript": "bank refuse karila, mrutyu praman achi, please help"}'
```

**Test guided mode next-question logic:**

```bash
curl -X POST http://localhost:8000/triage/next-question \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "please help, death hogaya",
    "relation_to_deceased": "mother",
    "bank_name": null
  }'
```

---

**Bonus: interactive API docs (free with FastAPI)**

FastAPI auto-generates a UI where you can test every endpoint without curl:

```
http://localhost:8000/docs
```

Start there — it's easier than writing curl commands manually.

---

**If you hit an import error** it's almost always the `routers/triage.py` file not being registered in `main.py` yet. Double check that file has:

```python
from routers import voice, debug, triage
app.include_router(triage.router)
```
