@echo off
echo =====================================================
echo  Autonomous Legal Reasoning Engine - Start Script
echo =====================================================
echo.

REM Check if data directories exist
if not exist "backend\data\uploads" mkdir backend\data\uploads
if not exist "backend\data\chroma" mkdir backend\data\chroma

echo Starting Backend on http://localhost:8000 ...
start "Legal Engine Backend" cmd /k "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend on http://localhost:3000 ...
start "Legal Engine Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo =====================================================
echo  Both servers are starting in separate windows.
echo  Open: http://localhost:3000
echo  API:  http://localhost:8000/docs
echo =====================================================
echo.
pause
