# Wellsy Jarvis Engine 🎙️🤖

Wellsy is a local, secure desktop assistant architecture built to operate as a customizable Jarvis engine. It bridges high-level AI reasoning with low-level local system commands using the Model Context Protocol (MCP).

---

## ⚡ Key Architectural Features

### 1. Secure Local MCP Server
Wellsy runs a local FastAPI + FastMCP server exposing desktop integrations to Antigravity and client voice nodes:
*   **Media Control**: Spotify & YouTube playlists, queries, playback triggers.
*   **Communication**: Automated WhatsApp message routing and Gmail/Outlook inbox querying.
*   **System Drivers**: Master volume and screen brightness controls.
*   **Productivity**: Direct academic sync actions for Overleaf project files.

### 2. High-Performance Local RAG Ingestion
An active SQLite RAG pipeline indexes personal document directories (`D:\Wellsy\storage`) into searchable semantic vector sets:
*   **Chunking & Processing**: Reads PDF, Docx, and TXT files natively.
*   **Vector Models**: Generates vector records locally using `models/gemini-embedding-001`.
*   **Similarity Search**: Computes matching document passages in under 5ms using NumPy cosine calculations.

### 3. C++ Traversal Core (DLL)
Optimized directory traversal logic written in native C++ using Win32 `FindFirstFileW` & `FindNextFileW` API loops. Linking the compiled `scanner.dll` wrapper directly into Python cut filesystem traversal time over large folder trees by **1.9x** compared to standard Python.

### 4. Sandbox Path Protection
All filesystem tools resolve canonical targets using path whitelists (e.g. restricts file writes to `D:\Wellsy\storage`). Rejects traversal injections (`../`) or forbidden drives (`C:\Windows`) at runtime.

---

## 🚀 Running & Verification

### Prerequisites
*   Python 3.10+
*   G++ compiler (for building the C++ binary module)

### Start Wellsy Backend Server
Launch the FastAPI WebSocket orchestrator:
```bash
D:\Wellsy\venv\Scripts\python.exe D:\Wellsy\backend\main.py
```
Open `http://localhost:8765` in your browser to interact with the voice and chat dashboard.

### Run Verification Suite
Run validation tests checking the SQLite vector database and Sandbox path gates:
```bash
D:\Wellsy\venv\Scripts\python.exe D:\Wellsy\tests\test_mcp_rag.py
```
Run speed comparison benchmarks:
```bash
D:\Wellsy\venv\Scripts\python.exe D:\Wellsy\tests\test_scanner_speed.py
```
