@echo off
echo.
echo ========================================
echo   ⚽ DSX LIVE GAME TRACKER
echo ========================================
echo.
echo Starting game tracker on http://localhost:8502
echo Parents can view at your local IP on port 8502
echo.
echo Press Ctrl+C to stop the tracker
echo ========================================
echo.

streamlit run live_game_tracker.py --server.port 8502 --server.address localhost

pause

