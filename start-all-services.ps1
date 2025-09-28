#!/usr/bin/env powershell
# Smart startup script for Mental Wellness Platform
# Fixes all hardcoded ports and starts services with proper configuration

Write-Host "🚀 Starting Mental Wellness Platform Services..." -ForegroundColor Green

# Load environment variables
$envFile = ".\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
        }
    }
    Write-Host "✅ Environment variables loaded" -ForegroundColor Green
}

# Get ports from environment or use defaults
$LLM_PORT = [Environment]::GetEnvironmentVariable("LLM_SERVICE_PORT")
if (-not $LLM_PORT) { $LLM_PORT = "8000" }

$INTENT_PORT = [Environment]::GetEnvironmentVariable("INTENT_SERVICE_PORT") 
if (-not $INTENT_PORT) { $INTENT_PORT = "8001" }

$ANALYTICS_PORT = [Environment]::GetEnvironmentVariable("ANALYTICS_SERVICE_PORT")
if (-not $ANALYTICS_PORT) { $ANALYTICS_PORT = "8002" }

Write-Host "🔧 Using ports: LLM=$LLM_PORT, Intent=$INTENT_PORT, Analytics=$ANALYTICS_PORT" -ForegroundColor Yellow

# Activate virtual environment
Write-Host "🐍 Activating virtual environment..." -ForegroundColor Blue
& .\venv\Scripts\Activate.ps1

# Start services in background
Write-Host "🤖 Starting LLM Service on port $LLM_PORT..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`& .\venv\Scripts\Activate.ps1; python -m uvicorn services.python.llm_service:app --host 0.0.0.0 --port $LLM_PORT --log-level info" -WindowStyle Minimized

Start-Sleep 2

Write-Host "🧠 Starting Intent Service on port $INTENT_PORT..." -ForegroundColor Blue  
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`& .\venv\Scripts\Activate.ps1; python -m uvicorn services.python.intent_service:app --host 0.0.0.0 --port $INTENT_PORT --log-level info" -WindowStyle Minimized

Start-Sleep 2

Write-Host "📊 Starting Analytics Service on port $ANALYTICS_PORT..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`& .\venv\Scripts\Activate.ps1; python -m uvicorn services.python.analytics_service:app --host 0.0.0.0 --port $ANALYTICS_PORT --log-level info" -WindowStyle Minimized

# Wait for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep 5

# Health check
Write-Host "🔍 Checking service health..." -ForegroundColor Blue
try {
    $llmHealth = Invoke-RestMethod -Uri "http://localhost:$LLM_PORT/health" -TimeoutSec 5
    Write-Host "✅ LLM Service: $($llmHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ LLM Service: Not responding" -ForegroundColor Red
}

try {
    $intentHealth = Invoke-RestMethod -Uri "http://localhost:$INTENT_PORT/health" -TimeoutSec 5  
    Write-Host "✅ Intent Service: $($intentHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Intent Service: Not responding" -ForegroundColor Red
}

try {
    $analyticsHealth = Invoke-RestMethod -Uri "http://localhost:$ANALYTICS_PORT/health" -TimeoutSec 5
    Write-Host "✅ Analytics Service: $($analyticsHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Analytics Service: Not responding" -ForegroundColor Red  
}

# Start frontend
Write-Host "🎨 Starting React Frontend..." -ForegroundColor Blue
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Minimized
Set-Location ..

Write-Host "🎉 All services started! Frontend will be available at http://localhost:3000" -ForegroundColor Green
Write-Host "📝 Check the minimized PowerShell windows for service logs" -ForegroundColor Yellow