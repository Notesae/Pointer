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
 $known=@('04E96BA5EDCA69DCDCBD7BB2B85607535F545B0CDD5DB3D3C6ED119D3977CADB','307D91B25ECC04A601C9C15E8AA37070FE3BDD0ED08363BCDCB6AFB6AE5D4EEF','B960B7C46A7CF5F95328A26C1855395D22612DC1F1BEF0EB9A02D944111E44FC','042637A6FA953293A5F9616EF1BA249CB4EDEBCDCA65CAF1FA6A60177377DE32','762A62175CDBBC132AF49128CD63818FFECD0FF9A36848D923672CACCA96DC72','560D8D46DFCDE8F0C2A6DDFCD458C7B2546F1D98C4392CE5E02DA33C34CAA9BF','DC9DB5762E684CCD01A8E21B6D995A67A234A76DBCA7E7FF793E7660908A499D','FB0406147587FBAC1BF9FFFDC62CE2EAAD8127FC631ADB6B2EB7C6AC6D4FF9A2')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.2 Violet STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
