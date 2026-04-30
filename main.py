import os
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import voice, triage, debug


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
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(triage.router)
app.include_router(debug.router)


@app.get("/")
async def root():
    return {"message": "Aji is listening. Send a voice message via WhatsApp."}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")
