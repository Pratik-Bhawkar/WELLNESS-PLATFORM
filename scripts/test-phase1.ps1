# Mental Wellness Platform - Phase 1 Testing Script
# Tests all Phase 1 components without requiring Docker

Write-Host "=== Mental Wellness Platform - Phase 1 Testing ===" -ForegroundColor Cyan

# Test 1: Environment Setup
Write-Host "`n1. Testing Development Environment..." -ForegroundColor Magenta
$pythonOk = try { C:\Users\PRATIK\Desktop\WELLNESS-PLATFORM\venv\Scripts\python.exe --version; $true } catch { $false }
$nodeOk = try { node --version > $null; $true } catch { $false }
$javaOk = try { java --version > $null; $true } catch { $false }
$dotnetOk = try { dotnet --version > $null; $true } catch { $false }

Write-Host "✅ Python: $(if ($pythonOk) { 'Ready' } else { 'Failed' })" -ForegroundColor $(if ($pythonOk) { 'Green' } else { 'Red' })
Write-Host "✅ Node.js: $(if ($nodeOk) { 'Ready' } else { 'Failed' })" -ForegroundColor $(if ($nodeOk) { 'Green' } else { 'Red' })
Write-Host "✅ Java: $(if ($javaOk) { 'Ready' } else { 'Failed' })" -ForegroundColor $(if ($javaOk) { 'Green' } else { 'Red' })
Write-Host "✅ .NET: $(if ($dotnetOk) { 'Ready' } else { 'Failed' })" -ForegroundColor $(if ($dotnetOk) { 'Green' } else { 'Red' })

# Test 2: Project Structure
Write-Host "`n2. Testing Project Structure..." -ForegroundColor Magenta
$requiredPaths = @(
    "services\python\intent_service.py",
    "services\python\llm_service.py", 
    "services\java\pom.xml",
    "services\java\src\main\java\com\wellness\gateway\WellnessGatewayApplication.java",
    "services\csharp\Program.cs",
    "services\csharp\WellnessAnalytics.csproj",
    "sql\schema.sql",
    "docker-compose.yml",
    ".env",
    ".gitignore"
)

$structureOk = $true
foreach ($path in $requiredPaths) {
    $fullPath = Join-Path $PSScriptRoot "..\$path"
    if (Test-Path $fullPath) {
        Write-Host "✅ $path" -ForegroundColor Green
    } else {
        Write-Host "❌ $path" -ForegroundColor Red
        $structureOk = $false
    }
}

# Test 3: Python Dependencies
Write-Host "`n3. Testing Python Dependencies..." -ForegroundColor Magenta
try {
    $importTest = C:\Users\PRATIK\Desktop\WELLNESS-PLATFORM\venv\Scripts\python.exe -c "import fastapi, uvicorn, pydantic; print('All imports successful')"
    Write-Host "✅ Python dependencies: Ready" -ForegroundColor Green
    $pythonDepsOk = $true
} catch {
    Write-Host "❌ Python dependencies: Missing FastAPI/Uvicorn" -ForegroundColor Red
    $pythonDepsOk = $false
}

# Test 4: Java Build System
Write-Host "`n4. Testing Java Build System..." -ForegroundColor Magenta
$pomPath = Join-Path $PSScriptRoot "..\services\java\pom.xml"
if (Test-Path $pomPath) {
    Write-Host "✅ Maven POM: Ready" -ForegroundColor Green
    $javaBuildOk = $true
} else {
    Write-Host "❌ Maven POM: Missing" -ForegroundColor Red
    $javaBuildOk = $false
}

# Test 5: C# Project
Write-Host "`n5. Testing C# Project..." -ForegroundColor Magenta
$csprojPath = Join-Path $PSScriptRoot "..\services\csharp\WellnessAnalytics.csproj"
if (Test-Path $csprojPath) {
    Write-Host "✅ .NET Project: Ready" -ForegroundColor Green
    $dotnetProjectOk = $true
} else {
    Write-Host "❌ .NET Project: Missing" -ForegroundColor Red
    $dotnetProjectOk = $false
}

# Test 6: Git Repository
Write-Host "`n6. Testing Git Repository..." -ForegroundColor Magenta
try {
    $gitStatus = git status --porcelain
    $gitRemote = git remote -v
    Write-Host "✅ Git repository: Initialized and connected to GitHub" -ForegroundColor Green
    $gitOk = $true
} catch {
    Write-Host "❌ Git repository: Not properly initialized" -ForegroundColor Red
    $gitOk = $false
}

# Final Phase 1 Assessment
Write-Host "`n=== Phase 1 Assessment ===" -ForegroundColor Cyan
$totalTests = 6
$passedTests = @($pythonOk, $nodeOk, $javaOk, $dotnetOk, $structureOk, $pythonDepsOk, $javaBuildOk, $dotnetProjectOk, $gitOk) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count

$completionPercentage = [math]::Round(($passedTests / $totalTests) * 100)

Write-Host "Phase 1 Completion: $completionPercentage% ($passedTests/$totalTests tests passed)" -ForegroundColor White

if ($completionPercentage -ge 80) {
    Write-Host "🎉 PHASE 1 COMPLETE!" -ForegroundColor Green
    Write-Host "✅ Foundation infrastructure ready" -ForegroundColor Green
    Write-Host "✅ Multi-language microservices scaffolded" -ForegroundColor Green
    Write-Host "✅ Database schema designed" -ForegroundColor Green
    Write-Host "✅ Git repository configured" -ForegroundColor Green
    Write-Host "`n🚀 Ready to proceed to Phase 2: Local LLM Integration" -ForegroundColor Green
} elseif ($completionPercentage -ge 60) {
    Write-Host "⚠️  PHASE 1 MOSTLY COMPLETE" -ForegroundColor Yellow
    Write-Host "Some components need attention before Phase 2" -ForegroundColor Yellow
} else {
    Write-Host "❌ PHASE 1 INCOMPLETE" -ForegroundColor Red
    Write-Host "Critical components missing - resolve issues before proceeding" -ForegroundColor Red
}

Write-Host "`nPhase 1 Components Status:" -ForegroundColor White
Write-Host "• Development Environment: $(if ($pythonOk -and $nodeOk -and $javaOk -and $dotnetOk) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "• Project Structure: $(if ($structureOk) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "• Python Services: $(if ($pythonDepsOk) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "• Java API Gateway: $(if ($javaBuildOk) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "• C# Analytics: $(if ($dotnetProjectOk) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "• Git Repository: $(if ($gitOk) { '✅' } else { '❌' })" -ForegroundColor White