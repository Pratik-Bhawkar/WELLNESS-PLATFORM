# Phase 2 Frontend Launch Script - Mental Wellness AI Platform
# Dependencies: Node.js, npm/yarn, React TypeScript components ready

Write-Host "=== Mental Wellness AI Platform - Phase 2 Frontend Launch ===" -ForegroundColor Cyan
Write-Host "Starting React TypeScript frontend with WebSocket integration..." -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "frontend\package.json")) {
    Write-Host "ERROR: frontend\package.json not found. Run from project root." -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location frontend

Write-Host "Installing React dependencies..." -ForegroundColor Yellow

# Try npm first
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Using npm to install dependencies..." -ForegroundColor Green
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== Frontend Configuration ===" -ForegroundColor Cyan
        Write-Host "React: 18.2.0 with TypeScript" -ForegroundColor White
        Write-Host "WebSocket: socket.io-client 4.7.4" -ForegroundColor White
        Write-Host "Styling: styled-components 6.1.8" -ForegroundColor White
        Write-Host "API Gateway: http://localhost:8002" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Starting development server..." -ForegroundColor Green
        Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        
        # Start the development server
        npm start
    } else {
        Write-Host "ERROR: npm install failed!" -ForegroundColor Red
        Write-Host "Please check Node.js installation and try again." -ForegroundColor Yellow
    }
} else {
    Write-Host "ERROR: npm not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual installation steps:" -ForegroundColor Cyan
    Write-Host "1. Install Node.js (LTS version recommended)" -ForegroundColor White
    Write-Host "2. cd frontend" -ForegroundColor White
    Write-Host "3. npm install" -ForegroundColor White
    Write-Host "4. npm start" -ForegroundColor White
}

# Return to project root
Set-Location ..