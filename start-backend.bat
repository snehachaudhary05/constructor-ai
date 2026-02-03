@echo off
echo ========================================
echo Starting AI Email Assistant Backend
echo ========================================
echo.

cd backend
call venv\Scripts\activate
echo Backend server starting on http://localhost:8000
echo.
echo Keep this window open!
echo Press Ctrl+C to stop the server
echo.
uvicorn app.main:app --reload

pause
