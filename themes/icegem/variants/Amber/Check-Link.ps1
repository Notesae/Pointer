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
 $known=@('8A7C09656197A9032C577D02B6248EA16C7DBBC8DD1D438C71F4CFEB22A461BA','EEDFD20BFC2AD5CBCA49A2A3B0E6BBC38FB282FAAFB5245868B8B1D2D39B8E1A','22EEC87EBFBEC3C82BF411919639EF52EFA0236F2446D2851C0288EE89987A85','1811F40C2A449306DB09F21E03BC0C5EDA9D3D7DAC8C5AB1894F834B5E4C7DB8','8363930A44FEA56123A3DDFC11343E202732C15726E21E9C86AB56AC71AE0C04','30A1A7C5DA94684B12E52119CC843E5F9E77C51326F0E0DAE5795DE7B5709E2A','E0E36332531DA505A74192E66DB1241C02B41B4577E052D9ACED0CBAD81EF738','34632FB7688F79CF1E342CBFAC857BA56E436587D3BAFC363B0D318A273FA25C')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Amber ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
