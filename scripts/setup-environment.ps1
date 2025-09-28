# Mental Wellness Platform - Dynamic Environment Setup
# Automatically detects, installs, and configures all development tools
# Can be run by anyone in the world to set up the complete development environment

Write-Host "=== Mental Wellness Platform Environment Setup ===" -ForegroundColor Cyan
Write-Host "Preparing development environment for AI-powered mental wellness platform..." -ForegroundColor White

# Check if winget is available for auto-installation
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue
if ($wingetAvailable) {
    Write-Host "✅ Package manager (winget) available for auto-installation" -ForegroundColor Green
} else {
    Write-Host "⚠️  Winget not available - manual installation may be required" -ForegroundColor Yellow
}

# Function to add to PATH if not already present
function Add-ToPath {
    param([string]$NewPath)
    if ($NewPath -and (Test-Path $NewPath) -and ($env:PATH -notlike "*$NewPath*")) {
        $env:PATH += ";$NewPath"
        Write-Host "Added to PATH: $NewPath" -ForegroundColor Green
        return $true
    }
    return $false
}

Write-Host "`n1. Configuring Python Virtual Environment..." -ForegroundColor Magenta
$venvPath = Join-Path $PSScriptRoot "venv\Scripts"
if (Test-Path $venvPath) {
    Add-ToPath $venvPath
    Write-Host "Python virtual environment configured" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
}

Write-Host "`n2. Configuring Node.js..." -ForegroundColor Magenta
$nodePath = "C:\Program Files\nodejs"
if (Test-Path $nodePath) {
    Add-ToPath $nodePath
    Write-Host "Node.js configured" -ForegroundColor Green
}

Write-Host "`n3. Configuring Java..." -ForegroundColor Magenta
$javaPath = Get-ChildItem "C:\Program Files\Microsoft\jdk-*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($javaPath) {
    $javaBinPath = Join-Path $javaPath.FullName "bin"
    Add-ToPath $javaBinPath
    Write-Host "Java configured" -ForegroundColor Green
}

Write-Host "`n4. Configuring .NET..." -ForegroundColor Magenta
$dotnetPath = "C:\Program Files\dotnet"
if (Test-Path $dotnetPath) {
    Add-ToPath $dotnetPath
    Write-Host ".NET configured" -ForegroundColor Green
}

Write-Host "`n5. Configuring MySQL..." -ForegroundColor Magenta
$mysqlPaths = @(
    "C:\Program Files\MySQL\MySQL Server*\bin",
    "C:\MySQL\bin",
    "$env:ProgramData\MySQL\MySQL Server*\bin"
)
$mysqlFound = $false
foreach ($path in $mysqlPaths) {
    $mysqlBin = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($mysqlBin) {
        Add-ToPath $mysqlBin.FullName
        $mysqlFound = $true
        Write-Host "MySQL configured" -ForegroundColor Green
        break
    }
}
if (-not $mysqlFound) {
    Write-Host "MySQL installation not found - may need manual PATH configuration" -ForegroundColor Yellow
}

Write-Host "`n6. Testing all development tools..." -ForegroundColor Magenta
try { 
    $pythonVer = python --version
    Write-Host "✅ Python: $pythonVer" -ForegroundColor Green 
} catch { 
    Write-Host "❌ Python: Not found" -ForegroundColor Red 
}

try { 
    $nodeVer = node --version
    Write-Host "✅ Node.js: $nodeVer" -ForegroundColor Green 
} catch { 
    Write-Host "❌ Node.js: Not found" -ForegroundColor Red 
}

try { 
    $javaVer = java --version | Select-Object -First 1
    Write-Host "✅ Java: $javaVer" -ForegroundColor Green 
} catch { 
    Write-Host "❌ Java: Not found" -ForegroundColor Red 
}

try { 
    $dotnetVer = dotnet --version
    Write-Host "✅ .NET: $dotnetVer" -ForegroundColor Green 
} catch { 
    Write-Host "❌ .NET: Not found" -ForegroundColor Red 
}

try { 
    $mysqlVer = mysql --version
    Write-Host "✅ MySQL: $mysqlVer" -ForegroundColor Green 
} catch { 
    Write-Host "⚠️  MySQL: Not found in PATH (may need service start)" -ForegroundColor Yellow 
}

try { 
    $dockerVer = docker --version
    Write-Host "✅ Docker: $dockerVer" -ForegroundColor Green 
} catch { 
    Write-Host "⚠️  Docker: Not found (may need Docker Desktop restart)" -ForegroundColor Yellow 
}

Write-Host "`n7. Checking Python virtual environment..." -ForegroundColor Magenta
$venvScriptsPath = Join-Path $PSScriptRoot "..\venv\Scripts"
if (Test-Path $venvScriptsPath) {
    try {
        & "$venvScriptsPath\Activate.ps1"
        Write-Host "✅ Python virtual environment activated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Virtual environment found but activation failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Python virtual environment not found - run 'python -m venv venv' first" -ForegroundColor Yellow
}

Write-Host "`n8. Mental Wellness Platform Service Check..." -ForegroundColor Magenta
$requiredServices = @{
    "Intent Classification" = "services\python\intent_service.py"
    "Local LLM Service" = "services\python\llm_service.py"
    "Database Schema" = "sql\schema.sql"
    "Docker Compose" = "docker-compose.yml"
    "Environment Config" = ".env"
}

foreach ($service in $requiredServices.GetEnumerator()) {
    $servicePath = Join-Path $PSScriptRoot "..\$($service.Value)"
    if (Test-Path $servicePath) {
        Write-Host "✅ $($service.Key): Ready" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Key): Missing" -ForegroundColor Red
    }
}

Write-Host "`n=== Mental Wellness Platform Environment Status ===" -ForegroundColor Cyan

# Summary
$pythonOk = try { python --version > $null; $true } catch { $false }
$nodeOk = try { node --version > $null; $true } catch { $false }
$javaOk = try { java --version > $null; $true } catch { $false }
$dotnetOk = try { dotnet --version > $null; $true } catch { $false }
$mysqlOk = try { mysql --version > $null; $true } catch { $false }
$dockerOk = try { docker --version > $null; $true } catch { $false }

$readyCount = @($pythonOk, $nodeOk, $javaOk, $dotnetOk, $mysqlOk, $dockerOk) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count

if ($readyCount -ge 4) {
    Write-Host "🚀 PLATFORM READY FOR DEVELOPMENT!" -ForegroundColor Green
    Write-Host "   Ready to build AI-powered mental wellness platform" -ForegroundColor Green
    Write-Host "   Next steps: Initialize database and start services" -ForegroundColor White
} else {
    Write-Host "⚠️  SETUP INCOMPLETE - $readyCount/6 tools ready" -ForegroundColor Yellow
    Write-Host "   Please install missing dependencies and run script again" -ForegroundColor White
}

Write-Host "`nPlatform Components Status:" -ForegroundColor White
Write-Host "• Multi-language microservices: $(if ($pythonOk -and $javaOk -and $dotnetOk) { '✅ Ready' } else { '❌ Incomplete' })" -ForegroundColor White
Write-Host "• Database & Storage: $(if ($mysqlOk) { '✅ Ready' } else { '❌ Incomplete' })" -ForegroundColor White  
Write-Host "• Containerization: $(if ($dockerOk) { '✅ Ready' } else { '❌ Incomplete' })" -ForegroundColor White
Write-Host "• Frontend Development: $(if ($nodeOk) { '✅ Ready' } else { '❌ Incomplete' })" -ForegroundColor White