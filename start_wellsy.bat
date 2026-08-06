@echo off
title Wellsy v2.0 — Jarvis Command Center Daemon
echo.
echo   =============================================
echo     W E L L S Y   v2.0
echo     Jarvis-Class AI Command Center Daemon
echo   =============================================
echo.
echo   Starting Wellsy Daemon...
echo.

cd /d D:\Wellsy
call venv\Scripts\activate.bat

echo   [1/3] Loading Multi-Agent Brain (4 Sub-Agents)...
echo   [2/3] Initializing Encrypted Memory DB & File Scanner...
echo   [3/3] Launching Dashboard on http://localhost:8765
echo.
echo   Open Dashboard : http://localhost:8765
echo   Use CLI        : python wellsy.py "command"
echo   =============================================
echo.

python backend\daemon.py
