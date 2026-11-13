@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Uninstall_Windows.ps1"
if errorlevel 1 pause
