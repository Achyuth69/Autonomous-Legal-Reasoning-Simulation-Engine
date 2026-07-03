@echo off
echo ===================================================
echo Autonomous Legal Reasoning Engine - Setup Script
echo ===================================================

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

echo.
echo 1. Setting up Backend...
echo ------------------------

cd backend

python -m venv venv
call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist "data\uploads" mkdir data\uploads
if not exist "data\chroma" mkdir data\chroma

echo Backend setup complete!

cd ..

echo.
echo 2. Setting up Frontend...
echo -------------------------

cd frontend

call npm install

echo Frontend setup complete!

cd ..

echo.
echo ===================================================
echo Setup Complete!
echo ===================================================
echo.
echo Next Steps:
echo 1. Add your OpenAI API key to backend\.env (OPENAI_API_KEY)
echo 2. Start PostgreSQL and Redis (or use Docker Compose)
echo 3. Run the application:
echo.
echo    Backend:  cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo    Frontend: cd frontend ^&^& npm run dev
echo.
echo    Or use Docker Compose: docker-compose up
echo.
echo Visit http://localhost:3000 to access the application
echo API docs at http://localhost:8000/docs
echo.
