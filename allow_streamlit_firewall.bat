@echo off
echo ============================================================
echo Configuring Windows Firewall for Streamlit
echo ============================================================
echo.
echo This will allow teammates on your network to access the dashboard
echo.

REM Add firewall rules for Streamlit
netsh advfirewall firewall add rule name="Streamlit Dashboard" dir=in action=allow protocol=TCP localport=8502
netsh advfirewall firewall add rule name="Streamlit Dashboard" dir=in action=allow program="%LocalAppData%\Programs\Python\Python313\python.exe" enable=yes

echo.
echo ============================================================
echo [OK] Firewall configured!
echo ============================================================
echo.
echo Your teammates can now access:
echo   http://192.168.1.78:8502
echo.
echo (Make sure they're on the same WiFi network as you)
echo.
pause

