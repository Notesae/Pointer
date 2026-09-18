$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 # 接受 4.3 的静态和动态链接光标，覆盖全部导出尺寸。
 $known=@('808F429C91BFF9E9F0111D2450C4CC8EE6DDD8786B7239E2964B35C57D8FA495','9BC66CE21F40807375531086B50890DEECDEA052627A7DD316D4C65D4DBE7A01','33146B5E6266538B447562C32A5C9903E0E3926A45B2E6987AC5D23FFBB255DC','B699A253D82DED40ECA7D83A3B7F7E8F4EF4FAB0B6837F03C45E2E59D4B14DD4','92174AEFA5A57897972F66FC343140E7D26DE9A053A12EE11282DC8A2202AA8E','ED9A62A262F7536AF6467704BFD767F05D572800CE360F4FF1A295C912AC101A','C7BBDBBF7B97B886DB2C2FBE6243BE0FF900BDC3FB5954BC25C142393C2C6067','79133648AE415B190F046731E0C311ED589446A90045F740558EA0DD9941E79B')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.3 RosePink ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
