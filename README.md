# 🪐 Wellsy — Multi-Agent AI Assistant

A Jarvis-class, voice-enabled, multi-agent AI assistant with a Solar System UI.

---

## Quick Start (Docker — Recommended for Sharing)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- A Google Gemini API key ([Get one free here](https://aistudio.google.com/apikey))

### Steps

1. **Clone or download this project**

2. **Create a `.env` file** in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Build and run:**
   ```bash
   docker compose up --build
   ```

4. **Open your browser:**
   ```
   http://localhost:8765
   ```

That's it! The Solar System dashboard will load with the multi-agent brain ready to chat.

---

## Quick Start (Native Windows — Full Features)

Running natively on Windows enables desktop automation (Spotify, WhatsApp, app control).

### Steps

1. **Install Python 3.13+** from [python.org](https://www.python.org/downloads/)

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run:**
   ```bash
   python backend/main.py
   ```

5. **Open your browser:**
   ```
   http://localhost:8765
   ```

---

## Feature Comparison

| Feature | Docker | Native Windows |
|---|:---:|:---:|
| Web Dashboard (Solar System UI) | ✅ | ✅ |
| Multi-Agent Brain (4 sub-agents) | ✅ | ✅ |
| Voice Output (Jenny TTS) | ✅ | ✅ |
| Chat + Gemini API | ✅ | ✅ |
| RAG Knowledge Base | ✅ | ✅ |
| Spotify Automation | ❌ | ✅ |
| WhatsApp Messaging | ❌ | ✅ |
| Desktop App Control | ❌ | ✅ |
| Volume / Brightness | ❌ | ✅ |
| Voice Input (Mic) | ❌ | ✅ |

---

## Architecture

```
User Voice/Text
      │
      ▼
┌─────────────┐
│  SUPERVISOR  │  ← Routes to the right specialist
└──────┬──────┘
       │
  ┌────┼────┬────────┐
  ▼    ▼    ▼        ▼
🎵    💬   🖥️       🔬
Media Comms OS/Sys Research
Agent Agent Agent   Agent
```

Built with: **LangGraph** · **Google Gemini** · **FastAPI** · **Edge TTS** · **Faster-Whisper**
