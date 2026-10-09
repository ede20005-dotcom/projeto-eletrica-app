@echo off
chcp 65001 > nul
title Antigravity Engenharia Elétrica & Renováveis — Iniciar App
echo ====================================================================
echo   ANTIGRAVITY ENGENHARIA ELÉTRICA & RENOVÁVEIS (APP DESKTOP/WEB)
echo ====================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Python detectado no sistema. Iniciando servidor local e janela nativa...
    python desktop_launcher.py
) else (
    echo [INFO] Abrindo aplicação diretamente no navegador padrão...
    start "" "%~dp0index.html"
)

echo.
exit /b 0
