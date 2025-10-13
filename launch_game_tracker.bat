@echo off
echo.
echo ========================================
echo   ⚽ DSX LIVE GAME TRACKER
echo ========================================
echo.
echo BEST FOR GAME DAY:
echo Use Streamlit Cloud URL on your phone!
echo https://dsx-tracker.streamlit.app
echo.
echo This local version is for testing only.
echo Starting on http://localhost:8502
echo.
echo Press Ctrl+C to stop the tracker
echo ========================================
echo.

python -m streamlit run live_game_tracker.py --server.port 8502 --server.address localhost

pause

