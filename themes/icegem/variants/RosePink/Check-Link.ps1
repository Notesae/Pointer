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
 $known=@('D933A6A87AD495AA0C3B9C396C0E764003851074FC2EB01B28BEAD77FA5FA3A4','957435486D6CE9F604F8CA777008EF00FBC28A6D0AA6DD823B54D261DF577E2B','42A04C427A0513BEB530AE6462DE429BEA31E8B5C7E3F2C9F2C4751EE6C4A8C5','6D3F5318B791CAF4D0DDEA5870CB23860E8F81F9D28AB0E33CA10B05033F4334','92310E16F5DC08D1ABBFDA72EF6F9122CA5F3D319306F17E6CC05943EB6BA02C','E9C96B76810FE9B1D394F0A50635C88663AEA715418DCF9768A72D2DCAF28B62','8FAE0395AAAF020B807E6A1D89CABD039DDA50C7BA267B1D0BF75FB949B0825B','55B18514437A74E3A2533DD731ACFB245EAC79F1CE077AB92DBC7B7A9AD01AD0')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 RosePink ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
