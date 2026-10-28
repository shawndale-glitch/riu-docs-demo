@echo off
rem Abre solo la visita guiada (sin la demo de consola), con textos en espanol.
rem Genera el sitio, lo sirve en un puerto local libre y abre la visita en Chrome o Firefox.
title RIU Genesis Documentation - visita guiada
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-demo.ps1" -TourOnly -Pace 0.3 -Lang es %*
echo.
pause
