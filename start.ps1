#!/usr/bin/env powershell
# Simple startup script for Unified Mental Wellness Platform
# GPU-only, no fallbacks, pure Phi-3-mini responses

Write-Host "=== Mental Wellness Platform - GPU Accelerated ===" -ForegroundColor Green

# Check GPU/CUDA
Write-Host "Checking GPU..." -ForegroundColor Yellow
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"NONE\"}'); exit(0 if torch.cuda.is_available() else 1)"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: CUDA/GPU not available. Fix PyTorch installation." -ForegroundColor Red
    exit 1
}

# Start unified API
Write-Host "Starting Unified API with Phi-3-mini..." -ForegroundColor Green
Set-Location "services\python"
python unified_api.py