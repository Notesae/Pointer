$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 # 接受 4.2 的静态和动态链接光标，覆盖全部导出尺寸。
 $known=@('FA7B7D20688DF0288F144691261BD7CF251C311FDBB0A71C2D164BF6DF4E5943','5243C451D9672D7ED73910DCE6FD8C7DFCC2195DA3293B7AED98B17104401B36','13DA1AF01A8C053CF438CF0BD776BCFC8F80BE8A6F8ADAEE57EA8C5FFE3E4167','844669253E4F47925928953D9BF4C969B1EFE18DE6490BBB9AA6F0C40F8E3CF9','C6D47A06919637EF1C293E0AB027A626770401C83032A006E1A51FECA6CC0AAB','46009708F033F4C3698CACEBD1C80643D5A83049EF1276B22F178043393B9A7D','D05046D4A2A95258F11D31550249CEFCE15295C997E666945FE4FFC1825C0003','3B8895813CAD7E1904E5B4E77E62F83CAE52CED549AC56B0DB344E7A4D7848D6')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.2 Mint STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
