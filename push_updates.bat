@echo off
REM Quick script to push all updates to GitHub

echo.
echo ========================================
echo   DSX Tracker - Push Updates to GitHub
echo ========================================
echo.

REM Add all changed files
echo Adding changed files...
git add .

REM Show what will be committed
echo.
echo Files to be committed:
git status --short

echo.
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update data files

echo.
echo Committing with message: %COMMIT_MSG%
git commit -m "%COMMIT_MSG%"

echo.
echo Pushing to GitHub...
git push

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo   SUCCESS! Updates pushed to GitHub
    echo   Streamlit Cloud will update in 60-90s
    echo ========================================
) else (
    echo ========================================
    echo   ERROR: Push failed!
    echo   Check your Git credentials
    echo ========================================
)

echo.
pause

