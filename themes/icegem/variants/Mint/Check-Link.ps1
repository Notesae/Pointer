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
 $known=@('164D3598D0B203556A64B0B3BE1A7C06122172AD5C0EF6A7B95C54C275D79E74','B2A20F39D80140C7A22A6C34934A7BA91383DB4C291E590119D0357E1908740D','D30C70D693F726B2405D22C02A4823253CC9116B7541A42C205F6B6C6B30C309','80F0FD8AC9250952C3E7272147236B78C0DE9C8BA7A33AE70E9559287D36F3D2','72AFB1CE24D3BB2136E4E8014445FD923C97A8368D749994C4532164F846CC64','A9DAB2F90D4F62D760436CEC86290F20BEC82725DC6633163B1F0F1966D81348','7C5658CB2BE90A5126DFB950A4645F119FB459085A4626DB0AEDB5E06158283D','1F09A8A8CEDA2DFDA9BBD155D2D102310B7A648906935ECC108453D6956372FC')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Mint ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
