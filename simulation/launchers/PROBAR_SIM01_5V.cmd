@echo off
cd /d "%~dp0"
echo Ejecutando SIM-01 5V con solver Normal. Esperar hasta que finalice.
start "" /wait "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" -norm -b -Run "SIM-01_calibrated_startup_5V.asc"
findstr /c:"Total elapsed time:" "SIM-01_calibrated_startup_5V.log" >nul
if errorlevel 1 (
 echo No se confirmo la finalizacion. Revisar el archivo .log.
 pause
 exit /b 1
)
start "" "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe" "SIM-01_calibrated_startup_5V.raw"
