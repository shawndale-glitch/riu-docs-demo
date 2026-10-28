@echo off
rem Demo de un solo clic de la POC docs-as-code, en espanol. Doble clic en este fichero.
rem Opciones adicionales, por ejemplo:  RUN-DEMO-ES.cmd -Pace 1.3
rem Guion para el presentador: demo\PRESENTER-NOTES.md
title RIU Genesis Documentation - demo de la POC
mode con: cols=110 lines=45 >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-demo.ps1" -Lang es %*
echo.
pause
