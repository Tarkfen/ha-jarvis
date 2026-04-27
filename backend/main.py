from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import get_settings
from backend.ha_client import HAClient
from backend.claude_client import JarvisClient

settings = get_settings()
ha_client: HAClient
jarvis: JarvisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ha_client, jarvis
    ha_client = HAClient(settings.ha_url, settings.ha_token)
    jarvis = JarvisClient(settings.anthropic_api_key, ha_client)
    yield
    await ha_client.close()


app = FastAPI(title="Jarvis", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        reply = await jarvis.chat(req.session_id, req.message)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def config():
    return {"picovoiceAccessKey": settings.picovoice_access_key or None}


@app.get("/api/health")
async def health():
    ha_ok = await ha_client.ping()
    return {
        "status": "ok" if ha_ok else "degraded",
        "home_assistant": "connected" if ha_ok else "unreachable",
        "ha_url": settings.ha_url,
        "anthropic": "configured",
    }


# Serve frontend — must be last
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
