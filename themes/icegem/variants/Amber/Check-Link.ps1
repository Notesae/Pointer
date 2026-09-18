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
 $known=@('8AF4036B8B8D9738D147E251FCA7268EB5627ACE004246533B737CA604EF8A31','64702F49C239F87D78817FF3D5BA5662A28130023045DCD87E30ED1A582F0FF8','D281488A71A3DEDB9AC1294A724BF0DF294647DCFDFC577AB8AE977364CBBA8E','18837F6698FE17045B16E8F064F5E12E8F12B0668296D77E164AC5FF6C3E61C4','829F8A7EF6F88EAC4F72D85F2F7CC1AEE1EB81E2CC137234F371AA9D4FCE56DF','921CFBEB223A1E8A0276CE51B73E27C493DEC8C41233D2DCBBDBACC2FA1C7A3C','95CB5C6586BBA2CB2907CD63DDA9780BD62E38A3B3D237059E2E801900FE65BF','DCA001FF84618A5FC94D77BBC2713D6AD102D199A094CE1B49A9AAC32D310961')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Amber ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
