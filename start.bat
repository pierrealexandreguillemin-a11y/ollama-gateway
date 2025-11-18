@echo off
echo ========================================
echo   Ollama Gateway - Starting...
echo ========================================
echo.
echo Gateway will start on http://localhost:4000
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
python main.py

pause
