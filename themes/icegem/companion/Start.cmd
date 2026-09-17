@echo off
set "ICEGEM_COMPANION_ROOT=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $root=$env:ICEGEM_COMPANION_ROOT; if(-not (Test-Path -LiteralPath (Join-Path $root 'IceGem-Companion.exe'))){& (Join-Path $root 'Build.ps1')}; Start-Process -FilePath (Join-Path $root 'IceGem-Companion.exe') -WindowStyle Hidden"
if errorlevel 1 pause
