"""
Wellsy Backend — FastAPI + WebSocket Server
The backbone that connects the frontend to the agent brain.
Serves the dashboard UI directly + handles WebSocket chat.
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from agent.brain import chat, rate_limiter
from langchain_core.messages import HumanMessage, AIMessage

# Voice output and input
try:
    from voice.tts import speak_async
    VOICE_ENABLED = True
    print("  [+] Voice output enabled (Jenny)")
except Exception as e:
    VOICE_ENABLED = False
    print(f"  [!] Voice output disabled: {e}")

try:
    from voice import VoiceListener
    STT_ENABLED = True
    print("  [+] Voice input (STT) ready")
except Exception as e:
    STT_ENABLED = False
    print(f"  [!] Voice input disabled: {e}")


# === FastAPI App ===
app = FastAPI(title="Wellsy Backend", version="0.1.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# === Conversation History ===
conversation_history: list = []
MAX_HISTORY = 50


# === Serve Dashboard ===
@app.get("/")
async def serve_dashboard():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/styles.css")
async def serve_css():
    return FileResponse(str(FRONTEND_DIR / "styles.css"), media_type="text/css")

@app.get("/renderer.js")
async def serve_js():
    return FileResponse(str(FRONTEND_DIR / "renderer.js"), media_type="application/javascript")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "rate_limits": rate_limiter.get_status(),
    }


@app.get("/api/rate-limits")
async def get_rate_limits():
    return rate_limiter.get_status()


# === 📁 Local RAG API Endpoints ===

@app.post("/api/rag/sync")
async def sync_rag_storage():
    """Trigger background scanning and indexing of D:\\Wellsy\\storage."""
    try:
        from tools.rag_pipeline import sync_storage_folder
        results = await asyncio.to_thread(sync_storage_folder)
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/rag/query")
async def query_rag_knowledge(q: str):
    """Query local knowledge database via text embedding vector search."""
    try:
        from tools.rag_pipeline import query_rag
        results = await asyncio.to_thread(query_rag, q)
        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# === WebSocket for Real-Time Chat ===
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"  [+] Client connected! Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"  [-] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    await websocket.send_json({
        "type": "status",
        "data": {
            "connected": True,
            "rate_limits": rate_limiter.get_status(),
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    })

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            if data.get("type") == "chat":
                user_message = data.get("message", "").strip()
                if not user_message:
                    continue

                await websocket.send_json({
                    "type": "thinking",
                    "data": {"status": "Wellsy is thinking..."}
                })

                try:
                    response_text, rate_status = await asyncio.to_thread(
                        _sync_chat, user_message
                    )

                    conversation_history.append({"role": "user", "content": user_message})
                    conversation_history.append({"role": "assistant", "content": response_text})

                    while len(conversation_history) > MAX_HISTORY * 2:
                        conversation_history.pop(0)

                    await websocket.send_json({
                        "type": "response",
                        "data": {
                            "message": response_text,
                            "rate_limits": rate_status,
                            "time": datetime.now().strftime("%H:%M:%S"),
                        }
                    })

                    # Speak the response!
                    if VOICE_ENABLED:
                        try:
                            await speak_async(response_text)
                        except Exception as ve:
                            print(f"  [!] Voice error: {ve}")

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": f"Oops, something went wrong: {str(e)}"}
                    })

            elif data.get("type") == "start_mic":
                if STT_ENABLED:
                    print("  [*] Starting mic listener...")
                    # We start the listener inside a background thread/loop
                    if not hasattr(websocket, 'listener') or websocket.listener is None:
                        # Define callback that pushes detected text to frontend as if user sent it
                        def on_speech(text):
                            print(f"  [Voice STT] Heard: {text}")
                            # Send transcribed text back to client so client prints it and routes it back
                            asyncio.run_coroutine_threadsafe(
                                websocket.send_json({
                                    "type": "speech_transcription",
                                    "data": {"message": text}
                                }),
                                asyncio.get_event_loop()
                            )
                        
                        try:
                            websocket.listener = VoiceListener()
                            websocket.listener.start(on_speech)
                            await websocket.send_json({
                                "type": "mic_status",
                                "data": {"active": True, "info": "Listening..."}
                            })
                        except Exception as mic_err:
                            await websocket.send_json({
                                "type": "error",
                                "data": {"message": f"Could not start mic: {mic_err}"}
                            })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Mic feature (STT) is disabled or faster-whisper not installed."}
                    })

            elif data.get("type") == "stop_mic":
                if hasattr(websocket, 'listener') and websocket.listener is not None:
                    print("  [*] Stopping mic listener...")
                    try:
                        websocket.listener.stop()
                    except Exception:
                        pass
                    websocket.listener = None
                await websocket.send_json({
                    "type": "mic_status",
                    "data": {"active": False, "info": "Mic off"}
                })

            elif data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "rate_limits": rate_limiter.get_status(),
                    }
                })

    except WebSocketDisconnect:
        if hasattr(websocket, 'listener') and websocket.listener is not None:
            try:
                websocket.listener.stop()
            except Exception:
                pass
        manager.disconnect(websocket)
    except Exception as e:
        print(f"  [!] WebSocket error: {e}")
        if hasattr(websocket, 'listener') and websocket.listener is not None:
            try:
                websocket.listener.stop()
            except Exception:
                pass
        manager.disconnect(websocket)


def _sync_chat(user_message: str) -> tuple[str, dict]:
    """Synchronous wrapper for the async chat function."""
    history = []
    for msg in conversation_history[-20:]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(chat(user_message, history))
    finally:
        loop.close()


# === Run Server ===
if __name__ == "__main__":
    print()
    print("  ============================================")
    print("    Wellsy is waking up...")
    print("  ============================================")
    print("    Dashboard : http://localhost:8765")
    print("    WebSocket : ws://localhost:8765/ws")
    print("    Open the link above in your browser!")
    print("  ============================================")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
