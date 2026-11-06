@echo off
echo ========================================================
echo   GoHard Cyber Defense System - Starting All Services
echo ========================================================
echo 1. Launching Website Server on http://localhost:3000 ...
start "Website Server (3000)" python -m http.server 3000 --directory "%~dp0website"

echo 2. Launching Streamlit AI Engine on http://localhost:8501 ...
start "Streamlit AI (8501)" python -m streamlit run "%~dp0app.py" --server.port 8501

timeout /t 3 >nul
start http://localhost:3000
echo.
echo [OK] Both servers are online!
echo Website:   http://localhost:3000
echo Streamlit: http://localhost:8501
echo ========================================================
