@echo off
echo ========================================
echo   AI Email Assistant - Starting...
echo ========================================
echo.
echo Starting Backend and Frontend servers...
echo.

:: Start backend in new window
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

:: Wait 5 seconds for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend in new window
start "Frontend Server" cmd /k "cd frontend && npm run dev"

:: Wait 5 seconds for frontend to start
timeout /t 5 /nobreak >nul

:: Open browser
echo.
echo Opening browser...
echo.
start http://localhost:5173

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Two Command Prompt windows have opened:
echo   1. Backend Server (port 8000)
echo   2. Frontend Server (port 5173)
echo.
echo Keep both windows open while using the app!
echo Close this window when done.
echo.
pause
