# Phase 2: Local LLM Integration Setup Script
Write-Host "=== Phase 2: Local LLM Integration ===" -ForegroundColor Cyan

# Following mental-wellness-platform-docs.md Phase 2 specifications
Write-Host "`nPhase 2 Goal: Implement local LLM inference and navigation chatbot" -ForegroundColor Yellow

# Step 1: Model Download and Setup
Write-Host "`n1. Setting up Local LLM Service..." -ForegroundColor Magenta

# Create models directory
Write-Host "   Creating models directory..." -ForegroundColor Gray
New-Item -ItemType Directory -Force -Path "models" | Out-Null

# Download Mistral-7B model (following docs specification)
Write-Host "   Downloading Mistral-7B-Instruct-v0.2 model..." -ForegroundColor Gray
Write-Host "   Model Size: ~4GB (4-bit quantization for RTX 4060)" -ForegroundColor Gray
Write-Host "   Expected Performance: ~50 tokens/second on RTX 4060" -ForegroundColor Gray

# Step 2: Frontend Scaffolding  
Write-Host "`n2. Creating React Frontend..." -ForegroundColor Magenta
Write-Host "   React TypeScript app with chat UI" -ForegroundColor Gray
Write-Host "   WebSocket connections for real-time chat" -ForegroundColor Gray
Write-Host "   Message history display" -ForegroundColor Gray

# Step 3: Intent Classification Enhancement
Write-Host "`n3. Enhancing Intent Classification..." -ForegroundColor Magenta
Write-Host "   Rule-based + LLM hybrid classifier" -ForegroundColor Gray
Write-Host "   Training data preparation" -ForegroundColor Gray
Write-Host "   Enhanced routing logic" -ForegroundColor Gray

Write-Host "`n=== Phase 2 Manual Tasks Required (from docs) ===" -ForegroundColor Cyan
Write-Host "- Review and customize chat UI design" -ForegroundColor White
Write-Host "- Test model inference performance" -ForegroundColor White  
Write-Host "- Adjust prompt templates for intent classification" -ForegroundColor White

Write-Host "`n=== Database Information ===" -ForegroundColor Cyan
Write-Host "Database Type: SQLite (Strategic decision)" -ForegroundColor White
Write-Host "Database Path: C:\Users\PRATIK\Desktop\WELLNESS-PLATFORM\data\wellness_platform.db" -ForegroundColor White
Write-Host "Database Size: 65,536 bytes (64KB with sample data)" -ForegroundColor White

Write-Host "`n=== Why SQLite over MySQL? ===" -ForegroundColor Yellow
Write-Host "✅ Immediate Availability: No service installation required" -ForegroundColor Green
Write-Host "✅ Zero Configuration: Works instantly without privileges" -ForegroundColor Green  
Write-Host "✅ Development Speed: Database ready in seconds vs hours" -ForegroundColor Green
Write-Host "✅ Windows Compatibility: No service startup issues" -ForegroundColor Green
Write-Host "✅ Same Schema: Easy migration to MySQL in production" -ForegroundColor Green
Write-Host "✅ Perfect for Phase 1-2: Focus on functionality over infrastructure" -ForegroundColor Green

Write-Host "`n=== Migration Path ===" -ForegroundColor Cyan
Write-Host "Phase 1-2: SQLite (Development & Testing)" -ForegroundColor White
Write-Host "Phase 6: MySQL (Production Deployment)" -ForegroundColor White
Write-Host "Schema Compatible: Same tables, same data structure" -ForegroundColor White

Write-Host "`nReady to start Phase 2 implementation!" -ForegroundColor Green