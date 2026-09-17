$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 $known=@('79813204E5261D4FAF91E2F3F1838E46CD75798FEE15D38AF546EA71375961D7','FE63FA3B9DCD774D692B2633304488F73E22A4B57AE7BF4B43D33BCEAF4BC814','1251210EE0B14CE8E45783F84BFBE2526374D889478A1673089B1263393FA842','C83B5CBB1114FFF0433A767CADCEEAE932FF8AAD414B1DA9A1E54C22CF814191')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.1 IceBlue STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
