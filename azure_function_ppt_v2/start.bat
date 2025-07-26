@echo off
echo Checking for processes using port 7076...

REM Find and kill processes using port 7076
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7076') do (
    echo Killing process %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo Starting PowerPoint Service v2...
npm start