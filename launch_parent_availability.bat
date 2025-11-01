@echo off
echo ========================================
echo DSX Parent Availability Page
echo ========================================
echo.
echo Starting parent availability page on port 8502...
echo Share this link with parents: http://localhost:8502
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
streamlit run parent_availability.py --server.port 8502





