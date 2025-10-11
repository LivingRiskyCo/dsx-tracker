@echo off
echo ========================================
echo DSX Data Updater
echo ========================================
echo.

echo [1/4] Updating division standings...
python fetch_gotsport_division.py
echo.

echo [2/4] Generating HTML report...
python create_html_report.py
echo.

echo [3/4] Committing to Git...
git add *.csv *.html
git commit -m "Data update %date%"
echo.

echo [4/4] Pushing to GitHub...
git push
echo.

echo ========================================
echo [DONE] Update complete!
echo ========================================
echo.
echo Streamlit Cloud will auto-deploy in 1-2 minutes.
echo Your teammates can refresh to see new data!
echo.
echo Local dashboard: http://localhost:8503
echo.
pause

