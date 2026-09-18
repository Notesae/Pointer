$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 # 接受 4.3 的静态和动态链接光标，覆盖全部导出尺寸。
 $known=@('79813204E5261D4FAF91E2F3F1838E46CD75798FEE15D38AF546EA71375961D7','5EFA4FAC3F4E28B647A718187B657F45E6CE071B7065FEBE8AAB7195510E1294','FE63FA3B9DCD774D692B2633304488F73E22A4B57AE7BF4B43D33BCEAF4BC814','00E8BDB482E7C28282255ED4ABABFB25F5C84CA0C0E1978D0331AD1302882C73','1251210EE0B14CE8E45783F84BFBE2526374D889478A1673089B1263393FA842','4A060C3460C468C07F65DFAC01A026AD864B6487E8645F9DAC04A53EC9BD68F4','C83B5CBB1114FFF0433A767CADCEEAE932FF8AAD414B1DA9A1E54C22CF814191','767953CA3C96016B70AFDE4B3AAC354B56B695699471720A368242FE15F8644B')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.3 IceBlue ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
