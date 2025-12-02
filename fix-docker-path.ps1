# PowerShell script to fix Docker PATH issue
# This script adds Docker to your current PowerShell session PATH

# Add Docker to PATH for current session
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"

# Test if docker command works
Write-Host "Testing Docker command..." -ForegroundColor Green
docker --version

Write-Host "Testing docker compose command..." -ForegroundColor Green  
docker compose version

Write-Host ""
Write-Host "Docker commands should now work in this PowerShell session!" -ForegroundColor Yellow
Write-Host "To make this permanent, add to your PowerShell profile." -ForegroundColor Yellow
Write-Host ""
Write-Host "Now you can run: docker compose up --build" -ForegroundColor Cyan
