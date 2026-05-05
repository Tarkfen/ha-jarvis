import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import get_settings
from backend.ha_client import HAClient
from backend.claude_client import JarvisClient

settings = get_settings()
ha_client: HAClient
jarvis: JarvisClient
oww_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ha_client, jarvis, oww_model
    ha_client = HAClient(settings.ha_url, settings.ha_token)
    jarvis = JarvisClient(settings.anthropic_api_key, ha_client)
    try:
        import openwakeword
        from openwakeword.model import Model as OWWModel
        openwakeword.utils.download_models(["hey_jarvis_v0.1"])
        oww_model = OWWModel(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        print("Wake word model loaded (hey_jarvis)")
    except Exception as e:
        print(f"Wake word model unavailable: {e}")
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


@app.get("/api/health")
async def health():
    ha_ok = await ha_client.ping()
    return {
        "status": "ok" if ha_ok else "degraded",
        "home_assistant": "connected" if ha_ok else "unreachable",
        "ha_url": settings.ha_url,
        "anthropic": "configured",
        "wake_word": "ready" if oww_model else "unavailable",
    }


@app.websocket("/ws/wake-word")
async def wake_word_ws(websocket: WebSocket):
    await websocket.accept()

    if oww_model is None:
        await websocket.send_text("unavailable")
        await websocket.close()
        return

    oww_model.reset()
    await websocket.send_text("ready")

    try:
        while True:
            data = await websocket.receive_bytes()
            audio = np.frombuffer(data, dtype=np.int16)
            prediction = await asyncio.to_thread(oww_model.predict, audio)
            for score in prediction.values():
                if score >= 0.5:
                    await websocket.send_text("detected")
                    oww_model.reset()
                    break
    except WebSocketDisconnect:
        pass


# Serve frontend — must be last
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
