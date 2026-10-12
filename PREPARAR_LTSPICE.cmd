@echo off
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0simulation\prepare_windows.ps1"
if errorlevel 1 echo No se completo la preparacion. Revisar el mensaje anterior.
pause
