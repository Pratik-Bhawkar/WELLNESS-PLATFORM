# Quick Phase 2 Demo Launch Script
# Starts LLM service only for testing the Phi-3-mini model

Write-Host "=== Phase 2 Demo: Phi-3-mini LLM Service ===" -ForegroundColor Cyan
Write-Host "Starting Local LLM service with GPU acceleration..." -ForegroundColor Green

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "=== Model Information ===" -ForegroundColor Cyan
Write-Host "Model: Microsoft Phi-3-mini-4k-instruct" -ForegroundColor White
Write-Host "Size: 7.1GB (3.8B parameters)" -ForegroundColor White
Write-Host "GPU: RTX 4060 (8GB VRAM)" -ForegroundColor White
Write-Host "Quantization: 4-bit BitsAndBytesConfig" -ForegroundColor White
Write-Host ""

Write-Host "Starting LLM service..." -ForegroundColor Green
Write-Host "Service will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

# Start the LLM service
python -m uvicorn services.python.llm_service:app --host 0.0.0.0 --port 8000 --log-level info