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
 $known=@('EF0490166E5966AB139EE66D6CBE45CDDFEB9107EC9C49545547D1BD0101BCC5','3F22B83191D460F2B07EC8A30E39D4C166F357E7DC79F9E59FB1F756AB1F7CC6','B121D9677F6FCFEE64243CF7229E6DC70227EFE374DAF5CE4D5B5F9B98B58D0B','578EF36E88F9368BCBC2B7560C6BA99EEE2A17BFA7480EC5E25A2492BCDFEF2E','CBD16DAFF0C4151F5C27ACD74C00CDF9893AA0B51D4C14C3C64BD190659A286A','2903F615C7E84F620CC5A829717B918F325209110136E8D67064C1FCA8E6CFF3','44F7A9F1E28E465DC870F33E22AA7489A43535FEDADE23BEB89EC6C62B6EFA98','C4895168C227524777250E8C3CE26F2662054A56F135F7F18930EBBBB5011E09')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 IceBlue ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
