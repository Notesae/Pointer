#requires -Version 5.1
<#
IceGem installer: current user only, no administrator rights required.
Install: .\Install-IceGem.ps1
Static:  .\Install-IceGem.ps1 -Mode Static
Restore: .\Install-IceGem.ps1 -Action Restore
Remove:  .\Install-IceGem.ps1 -Action Uninstall
API: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-systemparametersinfow
#>
[CmdletBinding()]
param(
    [ValidateSet('Install','Restore','Uninstall')][string]$Action='Install',
    [ValidateSet('Gentle','Static')][string]$Mode='Gentle',
    [ValidateSet('multi','32','48','64')][string]$Size='multi',
    [string]$SourceRoot='',
    [switch]$OpenSettings
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if($env:OS -ne 'Windows_NT'){throw 'This script requires Windows.'}
# Resolve paths in the script body, and reject empty values before Join-Path.
$scriptFile=$MyInvocation.MyCommand.Path
if([string]::IsNullOrWhiteSpace($SourceRoot)){
    if(-not [string]::IsNullOrWhiteSpace($PSScriptRoot)){$SourceRoot=$PSScriptRoot}
    elseif(-not [string]::IsNullOrWhiteSpace($scriptFile)){$SourceRoot=[IO.Path]::GetDirectoryName($scriptFile)}
    else {throw 'Cannot locate the script directory. Launch Install.cmd from the extracted IceGem folder.'}
}
$SourceRoot=[IO.Path]::GetFullPath($SourceRoot)
$localData=[Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
if([string]::IsNullOrWhiteSpace($localData)){$localData=$env:LOCALAPPDATA}
if([string]::IsNullOrWhiteSpace($localData)){throw 'Windows did not provide a LocalApplicationData directory.'}
$root=Join-Path -Path $localData -ChildPath 'IceGem-Managed'
$backupRoot=Join-Path -Path $localData -ChildPath 'IceGem-Backups'
Write-Host "IceGem 4.0 Mint installer | Source: $SourceRoot"
Write-Host "User data: $localData"
$baseline=Join-Path $backupRoot 'Before-IceGem.clixml'
$marker=Join-Path $root '.icegem-managed'
$owner='IceGem-Installer-v2'
$cursorKey='Control Panel\Cursors'
$schemeKey='Control Panel\Cursors\Schemes'
$slots=@('Arrow','Help','AppStarting','Wait','Crosshair','IBeam','NWPen','No','SizeNS','SizeWE','SizeNWSE','SizeNESW','SizeAll','UpArrow','Hand','Pin','Person')
$states=@('normal','help','working','busy','precision','text','handwriting','unavailable','resize-ns','resize-ew','resize-nwse','resize-nesw','move','alternate','link','location','person')
$schemeNames=@(foreach($prefix in @('IceGem Managed','IceGem IceBlue','IceGem Violet','IceGem RosePink','IceGem Mint','IceGem Amber')){foreach($s in @('multi','32','48','64')){foreach($m in @('Static','Gentle')){"$prefix $m ($s)"}}})
if(-not ('IceGemNativeV2' -as [type])){
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class IceGemNativeV2 {
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
 [return: MarshalAs(UnmanagedType.Bool)]
 public static extern bool SystemParametersInfo(uint action,uint param,IntPtr data,uint flags);
 [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
 public static extern IntPtr LoadImage(IntPtr instance,string file,uint type,int width,int height,uint flags);
 [DllImport("user32.dll")]
 [return: MarshalAs(UnmanagedType.Bool)]
 public static extern bool DestroyCursor(IntPtr cursor);
}
'@
}
function Refresh-Cursors {
    if(-not [IceGemNativeV2]::SystemParametersInfo(0x57,0,[IntPtr]::Zero,2)){
        throw "Windows cursor refresh failed. Win32 error: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
    }
}
function Capture-Settings {
    $records=@()
    foreach($entry in @(@{Path=$cursorKey;Names=@('','Scheme Source')+$slots},@{Path=$schemeKey;Names=$schemeNames})){
        $key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($entry.Path)
        try {
            foreach($name in $entry.Names){
                $exists=($null -ne $key -and $key.GetValueNames() -contains $name)
                $kind='String';$data=$null
                if($exists){
                    $kind=$key.GetValueKind($name).ToString()
                    $data=$key.GetValue($name,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
                }
                $records += [pscustomobject]@{Path=$entry.Path;Name=$name;Exists=$exists;Kind=$kind;Data=$data}
            }
        } finally {if($null -ne $key){$key.Dispose()}}
    }
    [pscustomobject]@{Owner=$owner;Version=2;Created=(Get-Date).ToString('o');Records=$records}
}
function Restore-Settings($snapshot) {
    if($snapshot.Owner -ne $owner -or $snapshot.Version -ne 2){throw 'Backup format is not recognized.'}
    foreach($record in $snapshot.Records){
        if($record.Path -notin @($cursorKey,$schemeKey)){throw 'Unexpected registry path in backup.'}
        $allowed=if($record.Path -eq $cursorKey){@('','Scheme Source')+$slots}else{$schemeNames}
        if($record.Name -notin $allowed){throw 'Unexpected registry value in backup.'}
    }
    foreach($record in $snapshot.Records){
        $key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($record.Path)
        try {
            if($record.Exists){$key.SetValue($record.Name,$record.Data,([Microsoft.Win32.RegistryValueKind][Enum]::Parse([Microsoft.Win32.RegistryValueKind], [string]$record.Kind)))}
            else {$key.DeleteValue($record.Name,$false)}
        } finally {$key.Dispose()}
    }
}
function Check-Cursor([string]$file) {
    foreach($n in @(32,48,64)){
        $handle=[IceGemNativeV2]::LoadImage([IntPtr]::Zero,$file,2,$n,$n,0x10)
        if($handle -eq [IntPtr]::Zero){throw "Windows could not load cursor: $file (size $n). Win32 error: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}
        [void][IceGemNativeV2]::DestroyCursor($handle)
    }
}
function Assert-ManagedRoot {
    if(Test-Path -LiteralPath $root){
        if(-not (Test-Path -LiteralPath $marker -PathType Leaf)){throw "Unrecognized existing folder; refusing to change it: $root"}
        if((Get-Content -LiteralPath $marker -Raw).Trim() -ne $owner){throw 'Installer ownership marker does not match.'}
        $items=@(Get-Item -LiteralPath $root)+@(Get-ChildItem -LiteralPath $root -Recurse -Force)
        foreach($item in $items){if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Managed folder contains a link/junction; refusing to change it.'}}
    }
}
$before=$null
$mutationStarted=$false
try {
    Assert-ManagedRoot
    if($Action -in @('Restore','Uninstall')){
        if(-not (Test-Path -LiteralPath $baseline -PathType Leaf)){throw "No original settings backup found: $baseline"}
        $original=Import-Clixml -LiteralPath $baseline
        $before=Capture-Settings
        $mutationStarted=$true
        Restore-Settings $original
        Refresh-Cursors
        $mutationStarted=$false
        if($Action -eq 'Uninstall'){
            $cleanup=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($schemeKey,$true)
            if($null -ne $cleanup){
                try {
                    foreach($title in $schemeNames){
                        $value=[string]$cleanup.GetValue($title)
                        if($value -and $value.Contains($root+'\')){$cleanup.DeleteValue($title,$false)}
                    }
                } finally {$cleanup.Dispose()}
            }
            if(Test-Path -LiteralPath $root){Remove-Item -LiteralPath $root -Recurse -Force}
            $archive=Join-Path $backupRoot ('Restored-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N')+'.clixml')
            Move-Item -LiteralPath $baseline -Destination $archive
            Write-Host 'IceGem uninstalled. Original settings restored; backup archived.' -ForegroundColor Green
        } else {Write-Host 'Original cursor settings restored. Installed resources remain available.' -ForegroundColor Green}
    } else {
        $source=Join-Path $SourceRoot "cursors\$Size"
        if(-not (Test-Path -LiteralPath $source -PathType Container)){throw "Cursor folder not found: $source. Use -SourceRoot to specify the extracted IceGem folder."}
        $files=@(foreach($state in $states){"icegem-$state.cur"})+@('icegem-normal.ani','icegem-working.ani','icegem-busy.ani')
        foreach($name in $files){
            $path=Join-Path $source $name
            if(-not (Test-Path -LiteralPath $path -PathType Leaf)){throw "Required file missing: $path"}
            Check-Cursor $path
        }
        $linkExpected=@{
            '32'='FA7B7D20688DF0288F144691261BD7CF251C311FDBB0A71C2D164BF6DF4E5943'
            '48'='13DA1AF01A8C053CF438CF0BD776BCFC8F80BE8A6F8ADAEE57EA8C5FFE3E4167'
            '64'='C6D47A06919637EF1C293E0AB027A626770401C83032A006E1A51FECA6CC0AAB'
            'multi'='D05046D4A2A95258F11D31550249CEFCE15295C997E666945FE4FFC1825C0003'
        }
        $linkSource=Join-Path $source 'icegem-link.cur'
        if((Get-FileHash -LiteralPath $linkSource -Algorithm SHA256).Hash -ne $linkExpected[$Size]){
            throw 'Link resource is not the 4.0 Mint strong gem click. Extract the complete versioned package into a NEW folder.'
        }
        $before=Capture-Settings
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        $stamp=(Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N')
        $before | Export-Clixml -LiteralPath (Join-Path $backupRoot "Before-$stamp.clixml") -Encoding UTF8
        if(-not (Test-Path -LiteralPath $baseline)){$before | Export-Clixml -LiteralPath $baseline -Encoding UTF8}
        else {$saved=Import-Clixml -LiteralPath $baseline;if($saved.Owner -ne $owner){throw 'Existing baseline is not an IceGem backup.'}}
        if(-not (Test-Path -LiteralPath $root)){
            New-Item -ItemType Directory -Path $root | Out-Null
            Set-Content -LiteralPath $marker -Value $owner -Encoding ASCII
        }
        $destination=Join-Path $root "$stamp-Mint-$Size"
        if($destination.Contains(',')){throw 'The user profile path contains a comma; scheme registration cannot safely encode this path.'}
        New-Item -ItemType Directory -Path $destination | Out-Null
        foreach($name in $files){
            $from=Join-Path $source $name;$to=Join-Path $destination $name
            Copy-Item -LiteralPath $from -Destination $to
            if((Get-FileHash -LiteralPath $from).Hash -ne (Get-FileHash -LiteralPath $to).Hash){throw "Copy verification failed: $name"}
        }
        $mutationStarted=$true
        $schemes=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($schemeKey)
        $selected=$null
        try {
            foreach($m in @('Static','Gentle')){
                $paths=@(foreach($state in $states){
                    $ext=if($m -eq 'Gentle' -and $state -in @('normal','working','busy')){'ani'}else{'cur'}
                    Join-Path $destination "icegem-$state.$ext"
                })
                $title="IceGem Mint $m ($Size)"
                $schemes.SetValue($title,($paths -join ','),[Microsoft.Win32.RegistryValueKind]::String)
                if($m -eq $Mode){$selected=$paths}
            }
        } finally {$schemes.Dispose()}
        $key=[Microsoft.Win32.Registry]::CurrentUser.CreateSubKey($cursorKey)
        try {
            for($i=0;$i -lt $slots.Count;$i++){$key.SetValue($slots[$i],$selected[$i],[Microsoft.Win32.RegistryValueKind]::ExpandString)}
            $key.SetValue('',"IceGem Mint $Mode ($Size)",[Microsoft.Win32.RegistryValueKind]::String)
            $key.SetValue('Scheme Source',1,[Microsoft.Win32.RegistryValueKind]::DWord)
        } finally {$key.Dispose()}
        Refresh-Cursors
        $verifyKey=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($cursorKey)
        try {$activeLink=[Environment]::ExpandEnvironmentVariables([string]$verifyKey.GetValue('Hand'))} finally {$verifyKey.Dispose()}
        $expectedLink=Join-Path $destination 'icegem-link.cur'
        if($activeLink -ne $expectedLink){throw "Link registry readback mismatch: $activeLink"}
        if((Get-FileHash -LiteralPath $activeLink -Algorithm SHA256).Hash -ne $linkExpected[$Size]){throw 'Installed Link hash mismatch.'}
        Write-Host '[VERIFIED] Link Select = 4.0 Mint STRONG GEM CLICK (file + registry).' -ForegroundColor Cyan
        Write-Host "Active Hand: $activeLink"
        $mutationStarted=$false
        Write-Host "Installed and applied: IceGem Mint $Mode ($Size)" -ForegroundColor Green
        Write-Host "Cursor files: $destination"
        Write-Host "Original settings backup: $baseline"
    }
    if($OpenSettings){Start-Process control.exe -ArgumentList 'main.cpl,,1'}
} catch {
    $problem=$_
    if($mutationStarted -and $null -ne $before){
        try {Restore-Settings $before;Refresh-Cursors;Write-Warning 'The operation failed. Previous cursor settings were restored.'}
        catch {Write-Warning "Automatic rollback failed. Backup location: $backupRoot. Restore your scheme in Mouse Properties. $($_.Exception.Message)"}
    }
    Write-Host ("[ERROR] " + $problem.Exception.Message) -ForegroundColor Red
    if($null -ne $problem.InvocationInfo){
        Write-Host $problem.InvocationInfo.PositionMessage
    }
    if($problem.ScriptStackTrace){Write-Host $problem.ScriptStackTrace}
    Write-Error -ErrorRecord $problem -ErrorAction Continue
    exit 1
}
