param(
    [string]$SpecPath = "lockers.spec",
    [switch]$SkipWiXInstall
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    Write-Host "Running PyInstaller build using $SpecPath"
    if (-not (Test-Path $SpecPath)) {
        throw "Unable to locate spec file '$SpecPath'"
    }

    & pyinstaller $SpecPath --noconfirm | Out-Host

    $distDir = Join-Path $repoRoot 'dist'
    $pyinstallerOutput = Join-Path $distDir 'lockers'
    if (-not (Test-Path $pyinstallerOutput)) {
        throw "PyInstaller output not found at $pyinstallerOutput"
    }

    $releaseDir = Join-Path $repoRoot 'dist/releases'
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

    $portableDir = Join-Path $releaseDir 'Lockers-Setup-x64'
    if (Test-Path $portableDir) {
        Remove-Item $portableDir -Recurse -Force
    }
    Copy-Item $pyinstallerOutput -Destination $portableDir -Recurse

    $mainExe = Join-Path $portableDir 'lockers.exe'
    if (Test-Path $mainExe) {
        Rename-Item $mainExe -NewName 'Lockers-Setup-x64.exe'
    }

    Write-Host "Preparing WiX toolset"
    if (-not (Get-Command candle.exe -ErrorAction SilentlyContinue)) {
        if ($SkipWiXInstall) {
            throw "WiX Toolset (candle.exe) not found. Install it or rerun without -SkipWiXInstall."
        }
        Write-Host "Installing WiX Toolset via Chocolatey"
        & choco install wixtoolset --no-progress --yes | Out-Host
    }

    $wixDir = Join-Path $distDir 'wix'
    New-Item -ItemType Directory -Force -Path $wixDir | Out-Null

    $heatFile = Join-Path $wixDir 'LockersHarvest.wxs'
    $componentGroup = 'LockerComponents'
    Write-Host "Harvesting PyInstaller output for MSI"
    & heat dir $portableDir -dr INSTALLFOLDER -cg $componentGroup -gg -g1 -srd -sreg -out $heatFile | Out-Host

    $productWxs = @"
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="Lockers Control" Language="1033" Version="0.1.0" Manufacturer="Lockers Control" UpgradeCode="{9C5B4CED-0C08-4B00-8AC9-24A4C7DA4904}">
    <Package InstallerVersion="500" Compressed="yes" InstallScope="perMachine" />
    <MediaTemplate />
    <MajorUpgrade DowngradeErrorMessage="A newer version of Lockers Control is already installed." />
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="LockersCL" />
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ProgramMenuDir" Name="Lockers Control" />
      </Directory>
    </Directory>
    <Feature Id="DefaultFeature" Level="1">
      <ComponentGroupRef Id="$componentGroup" />
      <ComponentRef Id="ShortcutComponent" />
    </Feature>
    <Component Id="ShortcutComponent" Guid="{7B8A0DFA-F83C-4AA3-9C90-8184CE4E3D1A}">
      <Shortcut Id="StartMenuShortcut" Directory="ProgramMenuDir" Name="Lockers Control" WorkingDirectory="INSTALLFOLDER" Target="[INSTALLFOLDER]Lockers-Setup-x64.exe" />
      <RemoveFolder Id="ProgramMenuDir" On="uninstall" />
      <RegistryValue Root="HKCU" Key="Software\\LockersCL" Name="Installed" Value="1" Type="integer" KeyPath="yes" />
    </Component>
  </Product>
</Wix>
"@

    $productFile = Join-Path $wixDir 'LockersProduct.wxs'
    Set-Content -Path $productFile -Value $productWxs -Encoding UTF8

    $objDir = Join-Path $wixDir 'obj'
    New-Item -ItemType Directory -Force -Path $objDir | Out-Null

    Write-Host "Compiling WiX sources"
    & candle.exe -nologo -out (Join-Path $objDir '\') $heatFile $productFile | Out-Host

    $msiPath = Join-Path $releaseDir 'Lockers-Setup-x64.msi'
    Write-Host "Linking MSI -> $msiPath"
    & light.exe -nologo -out $msiPath (Join-Path $objDir '*.wixobj') | Out-Host

    Write-Host "Generating SHA256SUMS"
    $hashFile = Join-Path $releaseDir 'SHA256SUMS'
    Get-ChildItem $releaseDir -File | Sort-Object Name | ForEach-Object {
        $hash = Get-FileHash $_.FullName -Algorithm SHA256
        "${($hash.Hash)}  $($_.Name)"
    } | Set-Content $hashFile -Encoding UTF8

}
finally {
    Pop-Location
}
