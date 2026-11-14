@echo off
echo ========================================================
echo   Starting ResearchPilot (Backend + Frontend)
echo ========================================================
echo.

echo Starting FastAPI Backend on http://localhost:8000 ...
start "ResearchPilot Backend" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting React Frontend on http://localhost:5173 ...
cd frontend
start "ResearchPilot Frontend" cmd /k "npm run dev"

echo.
echo Both services are launching in separate windows!
echo - Dashboard UI: http://localhost:5173
echo - API Docs:     http://localhost:8000/docs
echo ========================================================
pause
