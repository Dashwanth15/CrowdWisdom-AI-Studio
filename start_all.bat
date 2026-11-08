@echo off
echo ========================================================
echo   Starting CrowdWisdom AI Studio Platform
echo   Launching Backend and Frontend concurrently...
echo ========================================================

start "CrowdWisdom Backend (Port 8000)" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload"
timeout /t 3 /nobreak >nul
start "CrowdWisdom Frontend (Port 5173)" cmd /k "cd frontend && npx vite --port 5173"

echo.
echo All services launched!
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173
echo.
echo You can keep these terminal windows open while working.
pause

