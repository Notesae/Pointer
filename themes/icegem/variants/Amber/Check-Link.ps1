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
 $known=@('F600360D933BFC99AAADA45D24E515E12B884C35A9A52D0E75861462296509CD','1AF0EA724770015EFF81CD18ECB9A8E45274A206F645167E1C543CAF02A36E8D','BE8562ACA86DD9ABE712B47B90582E86388A007EC5A806977CB4F508B59C0702','CC1215BC0C4303A0F94BB1A5BA48B82AF9539850B36E3C5CA556C689B99728FE','54F3CB7D9F3F6FB35259302BB6709D4E93D8171760D6806BFBBAC59D67105D11','F9BDC1B1DE651E404C9CE6BD2911A72909BCDD060EE1CA3F4BEEFB5EF90CEDF7','1DE1AA53498AC7CA728129AD617FA8A040729788C384C1932EEC86D8019D557A','2D7A89113F07EFB7DF7B8EC8D5F41344ECD9BF74310E7DC5C710E4622EECA8A7')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.2 Amber STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
