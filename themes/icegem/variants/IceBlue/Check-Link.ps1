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
 $known=@('834934943873302A26104311A80997F1397547DE8A3D212F2199ABC3F1C6E8DA','7ABA82C8408A76F76E39AC9C4041CBC161EAFB3F614DC23C5C651BD85A70917A','EAFD7D08850702A8AC9EF86392C2952644B91112CD4BC867C4A27528226D43E9','252E4C53134BF61AA377D5F38AC02ABD553248565F61433AE9DFA75C9CF674B8','87AF247F8719E0B558B1B5F0CC83AF994A41D291914B6DAA2B85DCA8A43488A0','0681A8F80627F443C4AF1D747AF838BFB62D2CF120CA83DCF7E23EC2291CD9D9','FCAC802B58D7D7138926ACED97D3EC8DCC902D405F49F4662CBD56FC27966238','6EE07F648CA81C1ECB49B97C9F76EBB65E8E189FEEC5996A15ACA1A95BBD20E3')
 if($hash -in $known){Write-Host '[MATCH] Active registry points to the 4.4 IceBlue ROTATING CRYSTAL.' -ForegroundColor Green;Write-Host 'If only one app still shows the old icon, fully restart that app and test again.'}
 else {Write-Host '[MISMATCH] Windows Hand currently points to a different cursor. Run Install.cmd in THIS extracted folder.' -ForegroundColor Yellow}
 Write-Host 'This checks files and registry, not the cursor currently drawn by an application.'
} catch {Write-Host $_ -ForegroundColor Red;exit 1}
