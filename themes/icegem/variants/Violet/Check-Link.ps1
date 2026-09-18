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
 $known=@('2F8EDBE56B27F7146767DBE26BA818B1703A1D6F2BB640A5356217A867E47B51','ECB79387ADF3B2121A122504EFD4DA6A906CA49028C681DC178E77924AB4C2BF','1E576CB82F445545CCE1E1FAAD3EAAD046DF715AB3834A9A3570A8E0270C4A58','B0B6BA43060C2D33078F5D08F756F8D35DBB2730AB45A65F53BD8051C82FB5A0','333E022005FF1B9D1C13D6C613FC030369F540604D899258973EDC8AE8ACF3BE','A6C5A33F62C6036467F445DF22DDFC9542778F07A9740A34BFB01385662CB638','0680724F8A108C3849A44B37E1F15F675F32A6AFCD5E13D11D1AC214310EF507','10FACD2B6D1622927F15A496D659018A89ADAECAB8436F809E061B0B650559CA')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Violet ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
