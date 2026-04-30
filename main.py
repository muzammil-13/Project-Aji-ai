from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import voice, debug, triage

load_dotenv()

app = FastAPI(
    title="Project Aji",
    description="Empathetic AI assistant for legal rights guidance — grief and banking vertical",
    version="0.1.0",
)

# CORS — restrict in production to WhatsApp webhook IPs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: lock down in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(debug.router)
app.include_router(triage.router)


@app.get("/")
async def root():
    return {"message": "Aji is listening. Send a voice message via WhatsApp."}
