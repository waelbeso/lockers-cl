param(
    [switch]$SkipInstall
)

if (-not $SkipInstall) {
    Write-Host "Ensuring Briefcase with Windows support is installed..."
    python -m pip install --upgrade "briefcase[windows]"
}

Write-Host "Creating Briefcase Windows project"
try {
    briefcase create windows
} catch {
    Write-Host "Briefcase create step reported an error (possibly already created); continuing..."
}

Write-Host "Building Windows app"
briefcase build windows

Write-Host "Packaging Windows app"
briefcase package windows

Write-Host "Collecting distributable artefacts"
New-Item -ItemType Directory -Path "dist/releases" -Force | Out-Null
Get-ChildItem -Path "build/lockers/windows" -Include *.msi,*.zip -Recurse | ForEach-Object {
    Copy-Item $_.FullName -Destination "dist/releases" -Force
}
