@echo off
echo ========================================================
echo   Starting CrowdWisdom AI Studio Backend
echo   FastAPI + Hermes Orchestrator on http://127.0.0.1:8000
echo ========================================================
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload
pause

