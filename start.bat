@echo off
echo ========================================
echo   Ollama Gateway - Starting...
echo ========================================
echo.
echo Gateway URL: http://localhost:4000
echo Dashboard:   http://localhost:4000/studio
echo.
echo Pour arreter le serveur:
echo   - Cliquez sur le bouton Stop dans le dashboard
echo   - OU appuyez sur Ctrl+C dans cette fenetre
echo.
echo ========================================
echo.

cd /d "%~dp0"
python main.py

echo.
echo ========================================
echo   Serveur arrete
echo ========================================
pause
