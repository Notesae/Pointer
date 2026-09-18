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
 $known=@('2E6854A9FE60008B8B248D3A65AEDB2465D5F31A77AFE6FA85B972292D1379DD','7C0A980C5A7D9858A41CC1736F833A7E2DE0F382DF002E00A2A4E0FFBD368760','28428C164E22AD293E294DD6F7F537B27549D04F9D23669B2560FE998FA0C214','5B066EB5E03AFD7AD77C45615FF1A2855A260B1B73E20A9CD110961C4EF0161E','DBE537D9C14B0F0A848AD7D882F700C88841AC7E2F1325FD907C565D6AF8D1DF','A1855D5BDFAA2AF951E60F12886372A49EA0FB86013BBE190DF27C2EF1A7DAC8','B95948DB38A1125398B2E00E08D2E7846AF93337B772D119EE0E4259D24EF8EB','7FCD8233EC4C5B620C0C1FB0CCB5977F299DFC212FF6B239E0F5B7862EFECBF3')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 RosePink ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
