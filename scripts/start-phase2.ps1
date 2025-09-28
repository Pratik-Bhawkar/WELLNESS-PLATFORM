# Phase 2 Pure Python Startup Script - Mental Wellness AI Platform
# Launches all Python services: LLM + Intent + Analytics, React Frontend

Write-Host "=== Mental Wellness AI Platform - Phase 2 Pure Python Startup ===" -ForegroundColor Cyan
Write-Host "Launching all Python services with Local LLM Integration (Phi-3-mini)..." -ForegroundColor Green

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found. Run setup-environment.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "=== Phase 2 Pure Python Architecture ===" -ForegroundColor Cyan
Write-Host "1. Python LLM Service (Phi-3-mini): http://localhost:8000" -ForegroundColor White
Write-Host "2. Python Intent Service: http://localhost:8001" -ForegroundColor White  
Write-Host "3. Python Analytics Service: http://localhost:8002" -ForegroundColor White
Write-Host "4. React Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""

# Start Python LLM Service (Phi-3-mini)
Write-Host "Starting Python LLM Service with Phi-3-mini..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; venv\Scripts\Activate.ps1; python -m uvicorn services.python.llm_service:app --host 0.0.0.0 --port 8000 --log-level info" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Python Intent Service  
Write-Host "Starting Python Intent Recognition Service..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; venv\Scripts\Activate.ps1; python -m uvicorn services.python.intent_service:app --host 0.0.0.0 --port 8001 --log-level info" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Python Analytics Service
Write-Host "Starting Python Analytics Service..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; venv\Scripts\Activate.ps1; python -m uvicorn services.python.analytics_service:app --host 0.0.0.0 --port 8002 --log-level info" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start React Frontend
Write-Host "Starting React Frontend..." -ForegroundColor Green
if (Test-Path "frontend\package.json") {
    Set-Location frontend
    
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        # Install dependencies if node_modules doesn't exist
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
            npm install
        }
        
        Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; npm start" -WindowStyle Normal
    } else {
        Write-Host "WARNING: npm not found. Frontend may not start." -ForegroundColor Yellow
    }
    
    Set-Location ..
}

Write-Host ""
Write-Host "=== All Python Services Started! ===" -ForegroundColor Green
Write-Host "Give services 30-60 seconds to fully initialize..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "- Main App: http://localhost:3000" -ForegroundColor White
Write-Host "- LLM API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "- Intent API: http://localhost:8001/docs" -ForegroundColor White
Write-Host "- Analytics API: http://localhost:8002/docs" -ForegroundColor White
Write-Host ""
Write-Host "=== Phase 2 Pure Python Features Ready ===" -ForegroundColor Green
Write-Host "✓ Local Phi-3-mini LLM with GPU acceleration" -ForegroundColor White
Write-Host "✓ Direct HTTP communication (no Java dependency)" -ForegroundColor White
Write-Host "✓ Intent recognition and mood tracking" -ForegroundColor White
Write-Host "✓ Real-time analytics with matplotlib" -ForegroundColor White
Write-Host "✓ Mental wellness conversation routing" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services or close terminal windows individually." -ForegroundColor Yellow

# Wait for user input
Read-Host "Press Enter to exit this script (services will continue running)"