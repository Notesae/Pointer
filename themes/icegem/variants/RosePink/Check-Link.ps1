$ErrorActionPreference='Stop'
try {
 $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Control Panel\Cursors')
 try {$scheme=$k.GetValue('');$hand=[Environment]::ExpandEnvironmentVariables([string]$k.GetValue('Hand'))} finally {$k.Dispose()}
 Write-Host "Scheme: $scheme"
 Write-Host "Active Hand: $hand"
 if([string]::IsNullOrWhiteSpace($hand) -or -not (Test-Path -LiteralPath $hand)){throw 'Active Hand path is empty or missing.'}
 $hash=(Get-FileHash -LiteralPath $hand -Algorithm SHA256).Hash
 Write-Host "SHA256: $hash"
 $known=@('808F429C91BFF9E9F0111D2450C4CC8EE6DDD8786B7239E2964B35C57D8FA495','33146B5E6266538B447562C32A5C9903E0E3926A45B2E6987AC5D23FFBB255DC','92174AEFA5A57897972F66FC343140E7D26DE9A053A12EE11282DC8A2202AA8E','C7BBDBBF7B97B886DB2C2FBE6243BE0FF900BDC3FB5954BC25C142393C2C6067')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.1 RosePink STRONG GEM CLICK.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
