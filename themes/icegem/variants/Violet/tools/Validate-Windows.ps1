param([string]$Directory=(Join-Path $PSScriptRoot '..\cursors\multi'))
$ErrorActionPreference='Stop'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class CursorCheck {
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
 public static extern IntPtr LoadImage(IntPtr h,string name,uint type,int cx,int cy,uint flags);
 [DllImport("user32.dll")] public static extern bool DestroyCursor(IntPtr h);
}
'@
$failed=0
foreach($file in Get-ChildItem $Directory -File){
 foreach($size in @(32,48,64)){
  $h=[CursorCheck]::LoadImage([IntPtr]::Zero,$file.FullName,2,$size,$size,0x10)
  if($h -eq [IntPtr]::Zero){$failed++;Write-Warning "$($file.Name) / $size failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
  else{[void][CursorCheck]::DestroyCursor($h);Write-Host "OK $($file.Name) / $size"}
 }
}
if($failed){throw "$failed cursor load checks failed"}
