@echo off
rem Open only the guided tour (no console demo): builds the site, serves it on a free
rem local port and opens the tour in Chrome or Firefox. Double-click this file.
rem Spanish captions: OPEN-TOUR-ES.cmd
title RIU Genesis Documentation - guided tour
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-demo.ps1" -TourOnly -Pace 0.3 %*
echo.
pause
