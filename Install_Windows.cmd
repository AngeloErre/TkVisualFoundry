@echo off
cd /d "%~dp0"
if defined VTS_PYTHON (
  "%VTS_PYTHON%" installation.py install-windows
) else (
  py -3.15 installation.py install-windows
)
if errorlevel 1 echo Installation failed. Python 3.15+ final is required.
pause
