# Build Script for Local AI Assistant
# Builds both main.exe and popup.exe, then copies popup.exe to main directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Local AI Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build popup.exe
Write-Host "[1/3] Building popup.exe..." -ForegroundColor Yellow
pyinstaller popup.spec --distpath dist_new --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: popup.exe build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Success: popup.exe built" -ForegroundColor Green
Write-Host ""

# Step 2: Build main.exe
Write-Host "[2/3] Building main.exe..." -ForegroundColor Yellow
pyinstaller main.spec --distpath dist_new --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: main.exe build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Success: main.exe built" -ForegroundColor Green
Write-Host ""

# Step 3: Copy popup.exe to main directory
Write-Host "[3/3] Copying popup.exe to main directory..." -ForegroundColor Yellow
Copy-Item "dist_new\popup.exe" -Destination "dist_new\main\popup.exe" -Force
Write-Host "Success: popup.exe copied" -ForegroundColor Green
Write-Host ""

# Show file sizes
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files in dist_new\main:" -ForegroundColor Cyan
Get-ChildItem "dist_new\main\*.exe" | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name): $sizeMB MB" -ForegroundColor White
}
Write-Host ""
Write-Host "Distribution folder: dist_new\main\" -ForegroundColor Yellow
Write-Host "Ready to deploy or test!" -ForegroundColor Green
