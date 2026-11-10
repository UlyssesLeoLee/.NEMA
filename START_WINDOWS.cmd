@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (py -3 start_local.py) else (python start_local.py)
if errorlevel 1 pause
