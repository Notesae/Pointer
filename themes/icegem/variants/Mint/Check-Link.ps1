$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 $known=@('FA7B7D20688DF0288F144691261BD7CF251C311FDBB0A71C2D164BF6DF4E5943','13DA1AF01A8C053CF438CF0BD776BCFC8F80BE8A6F8ADAEE57EA8C5FFE3E4167','C6D47A06919637EF1C293E0AB027A626770401C83032A006E1A51FECA6CC0AAB','D05046D4A2A95258F11D31550249CEFCE15295C997E666945FE4FFC1825C0003')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.1 Mint STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
