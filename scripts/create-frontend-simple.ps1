# Phase 2 Frontend Creation - Simplified Version
Write-Host "=== Phase 2: Creating React Frontend ===" -ForegroundColor Cyan

Write-Host "`nFollowing CLI Automation Guide Phase 2:" -ForegroundColor Yellow
Write-Host "- React TypeScript app with chat UI" -ForegroundColor Gray
Write-Host "- WebSocket connections for real-time chat" -ForegroundColor Gray  
Write-Host "- Message history display" -ForegroundColor Gray

# Step 1: Check Node.js
Write-Host "`nStep 1: Checking Node.js..." -ForegroundColor Magenta
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue

if ($nodeCheck) {
    $nodeVersion = node --version
    Write-Host "Node.js detected: $nodeVersion" -ForegroundColor Green
    
    # Step 2: Create React App
    Write-Host "`nStep 2: Creating React TypeScript App..." -ForegroundColor Magenta
    npx create-react-app frontend --template typescript --use-npm
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "React app created successfully!" -ForegroundColor Green
    } else {
        Write-Host "React app creation failed" -ForegroundColor Red
    }
    
} else {
    Write-Host "Node.js not found - creating manual structure" -ForegroundColor Yellow
    
    # Create manual structure
    New-Item -ItemType Directory -Force -Path "frontend" | Out-Null
    New-Item -ItemType Directory -Force -Path "frontend/src" | Out-Null
    New-Item -ItemType Directory -Force -Path "frontend/src/components" | Out-Null
    New-Item -ItemType Directory -Force -Path "frontend/src/services" | Out-Null
    New-Item -ItemType Directory -Force -Path "frontend/public" | Out-Null
    
    Write-Host "Manual frontend structure created" -ForegroundColor Green
}

Write-Host "`n=== Phase 2 Frontend Status ===" -ForegroundColor Cyan
Write-Host "Ready for chat component implementation" -ForegroundColor Green