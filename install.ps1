# termi — your Terminal Friend 💛 · Windows/PowerShell installer (ORACLE P12)
# Windows-NATIVE flow NOT live-verified yet (no Windows box) — pwsh mechanics
# verified on macOS PowerShell 7.6. Honest coverage: `termi env` after install.

if ($IsMacOS -or $IsLinux) {
    # pwsh on unix: the POSIX installer is the real path
    & "$PSScriptRoot/install.sh"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Hey friend — termi here." -ForegroundColor Cyan
Write-Host ""
Write-Host "Termi can set up PowerShell itself (typo recovery, env doctor, profiles)."
Write-Host "But honestly? The full experience — and most serious dev tooling — lives in"
Write-Host "a Linux world. Windows ships a REAL one built in: WSL. Not scary, one"
Write-Host "command, and you keep Windows exactly as is." -ForegroundColor Green
Write-Host ""

$py = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
$pyOk = $false
if ($py) {
    & $py.Source -c "import tomllib" 2>$null
    $pyOk = $?
}
if (-not $pyOk) {
    Write-Host "termi needs Python >= 3.11:  winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 2
}

$dest = Join-Path $env:LOCALAPPDATA "termi"
New-Item -ItemType Directory -Force -Path (Join-Path $dest "bin") | Out-Null
Copy-Item -Recurse -Force "$PSScriptRoot/bin", "$PSScriptRoot/packs", "$PSScriptRoot/support", "$PSScriptRoot/skills" $dest
# a .cmd shim so `termi` works from any Windows shell
Set-Content -Path (Join-Path $dest "bin/termi.cmd") -Value "@echo off`r`npython `"%LOCALAPPDATA%\termi\bin\termi`" %*"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$binPath = Join-Path $dest "bin"
if ($userPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binPath", "User")
    Write-Host "✓ added $binPath to your user PATH (new terminals pick it up)"
}
Write-Host "✓ termi installed → $binPath" -ForegroundColor Green
Write-Host ""

& $py.Source (Join-Path $dest "bin/termi") env

Write-Host ""
$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if ($wsl -and (wsl --status 2>$null)) {
    Write-Host "WSL detected — run termi inside it too:" -ForegroundColor Green
    Write-Host "  wsl"
    Write-Host "  git clone https://github.com/fire17/termi && cd termi && ./install.sh"
} else {
    $ans = Read-Host "Install WSL now? Needs admin + one reboot [y/N]"
    if ($ans -eq "y") { wsl --install }
    else { Write-Host "When ready:  wsl --install   (docs: learn.microsoft.com/windows/wsl/install)" }
}
