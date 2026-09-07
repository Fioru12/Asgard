@echo off
title Asgard Cyber Suite - Portale Web Locale
echo ========================================================
echo   Avvio del Portale Web Asgard Cyber Suite (Apple-Grade)
echo ========================================================
echo.
echo Il sito web sara' accessibile all'indirizzo:
echo   http://localhost:8080
echo.
echo Premi CTRL+C per arrestare il server locale.
echo.

REM Avvia il browser predefinito dopo 1 secondo
start "" "http://localhost:8080"

REM Avvia il server HTTP di Python sulla cartella website
python -m http.server 8080 --directory "%~dp0"
pause
