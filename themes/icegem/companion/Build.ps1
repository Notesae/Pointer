# 将托盘程序编译到当前目录，不需要 SDK、管理员权限或修改系统设置。
$ErrorActionPreference='Stop'
$compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if(-not (Test-Path -LiteralPath $compiler)){throw 'Windows .NET Framework 4.x x64 compiler is required.'}
& $compiler /nologo /target:exe /platform:x64 /optimize+ /out:"$PSScriptRoot\IceGem-Companion.exe" /reference:System.Drawing.dll /reference:System.Windows.Forms.dll "$PSScriptRoot\Native.cs" "$PSScriptRoot\Motion.cs" "$PSScriptRoot\Program.cs"
if($LASTEXITCODE -ne 0){throw 'Companion compilation failed.'}
