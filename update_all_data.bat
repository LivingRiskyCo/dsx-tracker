@echo off
REM Comprehensive data update script for DSX Opponent Tracker
REM Updates all leagues, teams, and analysis in one command

echo ====================================================================
echo DSX OPPONENT TRACKER - ONE-CLICK DATA UPDATE
echo ====================================================================
echo.

python update_all_data.py

echo.
echo Press any key to exit...
pause >nul

