@echo off
setlocal DisableDelayedExpansion
title IceGem Cursor Installer
set "ICEGEM_SCRIPT=%~dp0Install-IceGem.ps1"
set "ICEGEM_SOURCE=%~dp0."
if not exist "%ICEGEM_SCRIPT%" (
    echo [ERROR] Install-IceGem.ps1 is missing from this folder.
    echo Extract both installer files into your IceGem folder.
    pause
    exit /b 1
)
if not exist "%ICEGEM_SOURCE%\cursors\multi\icegem-normal.cur" (
    echo [ERROR] The cursors folder is missing.
    echo Place these installer files beside the cursors folder.
    pause
    exit /b 1
)
echo Installing IceGem cursors...
echo.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%ICEGEM_SCRIPT%" -SourceRoot "%ICEGEM_SOURCE%" %*
set "ICEGEM_RESULT=%ERRORLEVEL%"
echo.
if "%ICEGEM_RESULT%"=="0" (
    echo [OK] Operation completed.
) else (
    echo [ERROR] Operation failed. Copy the error and line number above.
)
echo.
pause
exit /b %ICEGEM_RESULT%
