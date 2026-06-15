@echo off
title GATE Coach Bot
cd /d D:\gate-coach-bot
echo Starting GATE Coach Bot... (close this window or press Ctrl+C to stop)
.venv\Scripts\python.exe -m app.main
echo.
echo Bot stopped.
pause
