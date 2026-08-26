@echo off
title GUJARAT POLICE - SCRB COMMAND GRID 2.0
color 0b
echo ============================================================
echo   GUJARAT POLICE - STATE CRIME RECORD BUREAU (SCRB)
echo   STARTING SELF-HOSTED 25 CCTV STREAMING SERVER & STREAMLIT...
echo ============================================================

start "Gujarat CCTV Server (Port 5000)" /min python local_cctv_server.py
timeout /t 2 /nobreak >nul

echo.
echo [OK] 25 CCTV Streams Active on http://localhost:5000
echo [OK] Launching THE INITIATIVE 2.0 Command Grid...
echo.

streamlit run app1.py
pause
