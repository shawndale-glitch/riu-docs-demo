@echo off
rem One-button demo of the docs-as-code POC. Double-click this file.
rem Options are passed through, for example:  RUN-DEMO.cmd -Lang es -Pace 1.3
rem See demo\PRESENTER-NOTES.md for the talk track.
title RIU Genesis Documentation - POC demo
mode con: cols=110 lines=45 >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-demo.ps1" %*
echo.
pause
