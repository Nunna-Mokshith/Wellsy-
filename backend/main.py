"""
Wellsy Backend — FastAPI + WebSocket Server
The backbone that connects the frontend to the agent brain.
Serves the dashboard UI directly + handles WebSocket chat.
"""
import sys
import re
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


@app.get("/api/health")
async def api_health():
    """Health check for Docker and monitoring."""
    return {"status": "ok", "version": "2.0.0", "time": datetime.now().isoformat()}


@app.get("/api/system")
async def get_system_stats():
    """Live CPU, RAM, Disk stats for the Command Center gauges."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:\\').percent
        battery = None
        bat = psutil.sensors_battery()
        if bat:
            battery = {"percent": bat.percent, "plugged": bat.power_plugged}
        return {"cpu": round(cpu), "ram": round(ram), "disk": round(disk), "battery": battery}
    except Exception as e:
        return {"cpu": 0, "ram": 0, "disk": 0, "battery": None, "error": str(e)}


@app.get("/api/agents")
async def get_agents_status():
    """Return current agent roster and active state."""
    return {
        "agents": [
            {"id": "media", "name": "Media Agent", "icon": "🎵", "status": "standby"},
            {"id": "comms", "name": "Comms Agent", "icon": "💬", "status": "standby"},
            {"id": "os", "name": "System Agent", "icon": "🖥️", "status": "standby"},
            {"id": "research", "name": "Research Agent", "icon": "🔬", "status": "standby"},
        ]
    }


from memory.memory_db import memory_db
from memory.file_scanner import file_scanner
from scheduler.scheduler import task_scheduler

# === Startup Lifecycle ===
@app.on_event("startup")
async def on_startup():
    print("  [+] Running passive file scanner check...")
    try:
        greeting_diff = file_scanner.generate_greeting_summary()
        if greeting_diff:
            print(f"  [+] File Diff: {greeting_diff}")
    except Exception as e:
        print(f"  [!] File scanner error: {e}")

    # Start Task Scheduler background loop
    asyncio.create_task(task_scheduler.start_scheduler_loop())


@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get persistent memory statistics."""
    try:
        return memory_db.get_stats()
    except Exception as e:
        return {"total_memories": 0, "error": str(e)}


@app.get("/api/schedules")
async def get_schedules():
    """List active scheduled background tasks."""
    try:
        return {"schedules": task_scheduler.list_schedules(include_disabled=True)}
    except Exception as e:
        return {"schedules": [], "error": str(e)}


@app.post("/api/schedules")
async def create_schedule(data: dict):
    """Add a new scheduled task."""
    try:
        res = task_scheduler.add_schedule(
            title=data.get("title", "Task"),
            action=data.get("action", "general"),
            trigger_time=data.get("trigger_time", "23:00"),
            schedule_type=data.get("schedule_type", "ONCE"),
            target=data.get("target")
        )
        return {"status": "success", "schedule": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    """Cancel a scheduled task."""
    try:
        success = task_scheduler.remove_schedule(schedule_id)
        return {"status": "success" if success else "not_found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


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

                    # Speak the response (sanitized for natural voice)
                    if VOICE_ENABLED:
                        try:
                            voice_text = sanitize_for_voice(response_text)
                            if voice_text.strip():
                                await speak_async(voice_text)
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


def sanitize_for_voice(text: str) -> str:
    """Aggressively strip URLs, file paths, markdown, code, emojis, and technical
    artifacts so TTS reads clean, natural spoken English only."""

    # 1. Remove entire code blocks (```...```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 2. Remove inline code (`...`)
    text = re.sub(r'`[^`]+`', '', text)

    # 3. Remove ALL URLs (http, https, ftp, ws, wss, with or without protocol)
    text = re.sub(r'(?:https?|ftp|wss?|file)://\S+', '', text)
    # Bare URLs like localhost:8765 or www.google.com/path
    text = re.sub(r'(?:localhost|(?:www\.)?[\w-]+\.(?:com|org|net|io|dev|co|ai|gov|edu))\S*', '', text)

    # 4. Remove Windows file paths (D:\..., C:\..., D:/...)
    text = re.sub(r'[A-Z]:[\\\/][\w\\\/.\-~]+', '', text)
    # 5. Remove Unix/Linux file paths (/home/..., /usr/..., etc.)
    text = re.sub(r'/(?:home|usr|var|tmp|etc|opt|mnt|media|proc|sys|dev|root|srv)[\w/.\-~]*', '', text)
    # 6. Remove any remaining path-like patterns (e.g., backend/agent/brain.py)
    text = re.sub(r'(?:[\w\-]+[/\\]){2,}[\w\-]+(?:\.\w+)?', '', text)

    # 7. Remove markdown links [text](url) — keep display text only
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 8. Remove markdown bold/italic markers
    text = re.sub(r'\*{1,3}', '', text)
    # 9. Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 10. Remove markdown tables (lines with pipes)
    text = re.sub(r'^\|.*\|$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*[-:]+\|[-:|]+$', '', text, flags=re.MULTILINE)
    # 11. Remove bullet point markers
    text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
    # 12. Remove numbered list markers (1. 2. etc.)
    text = re.sub(r'^\s*\d+[.)]\s+', '', text, flags=re.MULTILINE)

    # 13. Remove emojis and special unicode symbols
    text = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0000FE00-\U0000FEFF\U0001FA00-\U0001FAFF\u200d\u2640\u2642\u2764\u2b50\u26a1\u2705\u274c\u2714\u2716\u25a1\u2500\u2715]+', '', text)

    # 14. Remove parenthetical technical details like (e.g., 127.0.0.1:8765)
    text = re.sub(r'\([^)]*(?:https?://|localhost|\.exe|\.py|\.js|\.css|\.html|\\\\|//)[^)]*\)', '', text)

    # 15. Remove leftover technical tokens (.exe, .py, .js, etc.)
    text = re.sub(r'\b\S+\.(?:exe|py|js|css|html|json|yaml|yml|toml|cfg|ini|log|txt|md|bat|sh|ps1)\b', '', text)

    # 16. Remove IP addresses and port numbers
    text = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b', '', text)

    # 17. Clean up resulting mess
    text = re.sub(r'\(\s*\)', '', text)        # Empty parentheses
    text = re.sub(r'\[\s*\]', '', text)        # Empty brackets
    text = re.sub(r':\s*$', '.', text, flags=re.MULTILINE)  # Trailing colons -> period
    text = re.sub(r'\n{3,}', '\n\n', text)     # Collapse blank lines
    text = re.sub(r'  +', ' ', text)           # Collapse spaces
    text = re.sub(r'^\s+$', '', text, flags=re.MULTILINE)  # Remove blank lines

    return text.strip()


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
