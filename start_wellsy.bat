@echo off
title Wellsy — Starting Up...
echo.
echo   =============================================
echo     W E L L S Y
echo     Your Personal AI Best Friend
echo   =============================================
echo.
echo   Starting Wellsy...
echo.

:: Activate virtual environment and start the server
cd /d D:\Wellsy
call venv\Scripts\activate.bat

echo   [1/2] Loading brain + 53 tools...
echo   [2/2] Starting server on http://localhost:8765
echo.
echo   Open your browser to http://localhost:8765
echo   Or just talk to Wellsy through voice!
echo.
echo   Press Ctrl+C to shut down Wellsy.
echo   =============================================
echo.

python backend\main.py
