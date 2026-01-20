# PRISM Brain Backend v3.0.0 (Live Probabilities) - Windows extractor
# Usage (PowerShell):
#   cd $HOME\Downloads
#   .\EXTRACT_WINDOWS.ps1

$pkg = "prism_brain_live_probabilities_v3_FIXED.tar.gz"
$target = "prism_brain_live_backend_v3"

if (!(Test-Path $pkg)) {
  Write-Host "ERROR: $pkg not found in current folder." -ForegroundColor Red
  exit 1
}

if (Test-Path $target) {
  Write-Host "Removing existing folder: $target" -ForegroundColor Yellow
  Remove-Item -Recurse -Force $target
}

New-Item -ItemType Directory -Force $target | Out-Null

tar -xzf $pkg -C $target

Write-Host "Extracted to .\\$target" -ForegroundColor Green
Write-Host "Now run: cd $target" -ForegroundColor Green
