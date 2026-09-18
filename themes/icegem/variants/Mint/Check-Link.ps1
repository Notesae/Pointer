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
 $known=@('6FBF6ADE69A3BFA3D305BEBABE5A559F36570AEFF30A0AAACAFD801E199ECB2A','08F883A455D90DFB4990A91F8DB5E12E3FA57C13B6505FCBC61C642A34F70194','85EB9BFF2BC349736B3C97B660C115D22A97A43DE4EFD6EAF24911B059A04222','FBBDE0A7F4FAD6ECEFCD866BF3A3C4B13CACFBEFD0131BA512DDC5F8BFA760AA','28EA939BA408ACD7D70C0B036435BF5C65AFC208C16F7AB7E39B570E5FA7EF86','20ACEC3210CA089F030D4A2D3FBB0722853CEFD3E62BBF02E8D8E6A611521561','40B0964F5BAFD42116C8B56E9C3E2FD685CEAAA09B2EDEE014218E8232757A5B','236E6C5EB4F0C47FE1BDBFCE8FD91CA9B341A7B819A353C4453085529469746E')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 Mint ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
