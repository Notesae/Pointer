$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 # 接受 4.4 的静态和动态链接光标，覆盖全部导出尺寸。
 $known=@('05027282471D5B9EDDE71FD0CFC510C24636B918567AD50F334D35774A3BFBEA','C0AA63628A941A7BC8A28310953B29D88E045D8065C5ADED6A1792AD3D0B6B14','43A8D8788C444687C8D823FF16D9B0FE0BD6E7C9470E276819DE5459EFAC97FF','E622CF01FF09565DB179A51BCD8D5D80894C22A5A856EDAB5180B68EA5588881','EB101EE4AED21C3A24AB019C8542BEA649357E50BF30609D74BEB6895A08B49B','91537801C1A636B1EE86289B43AAAF0AE2AA02E1CEADB14F95EE0FF01C6357E7','A88B15A249AB9682D77C768631D2494D66EA22DFA7AEF6F80903351608C8733E','4711255B95BC52C192B80FD5A448152F43B33B1E771222F011F18FABF179DC85')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Violet ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
