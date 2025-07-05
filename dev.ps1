#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Email Ledger POC - Development Scripts

.DESCRIPTION
    PowerShell script for common development tasks in the Email Ledger POC project.

.PARAMETER Command
    The command to run. Use 'help' to see all available commands.

.EXAMPLE
    .\dev.ps1 help
    .\dev.ps1 install
    .\dev.ps1 run-api
#>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Colors for output
$Colors = @{
    Info = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Info
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Success
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Warning
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $Colors.Error
}

function Show-Help {
    Write-Host "Email Ledger POC - Development Commands" -ForegroundColor $Colors.Info
    Write-Host "==========================================" -ForegroundColor $Colors.Info
    Write-Host ""
    
    $commands = @{
        "help" = "Show this help message"
        "install" = "Install the package in development mode"
        "install-dev" = "Install with development dependencies"
        "install-full" = "Install with all dependencies"
        "test" = "Run tests"
        "test-cov" = "Run tests with coverage"
        "lint" = "Run linting checks"
        "format" = "Format code with black and isort"
        "format-check" = "Check code formatting"
        "setup" = "Setup database tables"
        "demo-data" = "Generate demo data"
        "clear-data" = "Clear demo data"
        "run-api" = "Start the API server"
        "run-api-dev" = "Start API server in development mode"
        "run-cli" = "Run CLI processor once"
        "run-cli-continuous" = "Run CLI processor continuously"
        "run-cli-setup" = "Run CLI setup"
        "docker-build" = "Build Docker image"
        "docker-run" = "Run with Docker Compose"
        "docker-stop" = "Stop Docker containers"
        "build" = "Build package for distribution"
        "clean" = "Clean build artifacts"
        "dev-setup" = "Complete development setup"
        "dev-test" = "Run full development test suite"
        "dev-run" = "Run development environment"
        "setup-gmail" = "Setup Gmail API credentials"
        "env-create" = "Create .env file from template"
        "env-check" = "Check environment variables"
        "quick-start" = "Quick start for development"
        "quick-test" = "Quick test run"
        "status" = "Show project status"
    }
    
    foreach ($cmd in $commands.GetEnumerator() | Sort-Object Key) {
        Write-Host ("{0,-20} {1}" -f $cmd.Key, $cmd.Value) -ForegroundColor $Colors.Info
    }
}

function Install-Package {
    Write-Info "Installing package in development mode..."
    pip install -e .
    Write-Success "Package installed successfully!"
}

function Install-Dev {
    Write-Info "Installing with development dependencies..."
    pip install -e ".[dev,test]"
    Write-Success "Development dependencies installed!"
}

function Install-Full {
    Write-Info "Installing with all dependencies..."
    pip install -r requirements.txt
    pip install -e ".[dev,test]"
    Write-Success "All dependencies installed!"
}

function Test-Package {
    Write-Info "Running tests..."
    python -m pytest tests/ -v
}

function Test-Coverage {
    Write-Info "Running tests with coverage..."
    python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
}

function Format-Code {
    Write-Info "Formatting code..."
    black src/ tests/ --line-length=88
    isort src/ tests/ --profile=black
    Write-Success "Code formatted!"
}

function Format-Check {
    Write-Info "Checking code formatting..."
    black src/ tests/ --line-length=88 --check
    isort src/ tests/ --profile=black --check
    Write-Success "Code formatting check passed!"
}

function Lint-Code {
    Write-Info "Running linting checks..."
    flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
    mypy src/ --ignore-missing-imports
    Write-Success "Linting passed!"
}

function Setup-Database {
    Write-Info "Setting up database tables..."
    python -m src.cli.main setup
}

function Generate-DemoData {
    Write-Info "Generating demo data..."
    python scripts/demo_data.py --count 50
}

function Clear-DemoData {
    Write-Info "Clearing demo data..."
    python scripts/demo_data.py --clear
}

function Start-API {
    Write-Info "Starting API server..."
    python -m src.app.api.app
}

function Start-APIDev {
    Write-Info "Starting API server in development mode..."
    Write-Info "API: http://localhost:8000"
    Write-Info "Docs: http://localhost:8000/docs"
    uvicorn src.app.api.app:app --reload --host 0.0.0.0 --port 8000
}

function Start-CLI {
    Write-Info "Running CLI processor once..."
    python -m src.cli.main process
}

function Start-CLIContinuous {
    Write-Info "Running CLI processor continuously..."
    python -m src.cli.main process --continuous
}

function Start-CLISetup {
    Write-Info "Running CLI setup..."
    python -m src.cli.main setup
}

function Build-Docker {
    Write-Info "Building Docker image..."
    docker build -t email-ledger-poc .
}

function Start-Docker {
    Write-Info "Starting with Docker Compose..."
    docker-compose up --build
}

function Stop-Docker {
    Write-Info "Stopping Docker containers..."
    docker-compose down
}

function Build-Package {
    Write-Info "Building package for distribution..."
    python build.py
}

function Clean-Build {
    Write-Info "Cleaning build artifacts..."
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    
    # Remove __pycache__ directories
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_
    }
    
    # Remove .pyc files
    Get-ChildItem -Recurse -File -Filter "*.pyc" | Remove-Item -Force
    
    Write-Success "✅ Build artifacts cleaned!"
}

function Setup-Dev {
    Write-Info "Setting up development environment..."
    pip install -e ".[dev,test]"
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Success ".env file created from template"
    }
    Write-Success "Development setup complete!"
    Write-Warning "📝 Please update .env with your configuration"
}

function Test-Dev {
    Write-Info "Running full development test suite..."
    Format-Check
    Lint-Code
    Test-Coverage
    Write-Success "✅ Development test suite complete!"
}

function Start-Dev {
    Write-Info "Starting development environment..."
    Write-Info "API: http://localhost:8000"
    Write-Info "Docs: http://localhost:8000/docs"
    uvicorn src.app.api.app:app --reload --host 0.0.0.0 --port 8000
}

function Setup-Gmail {
    Write-Info "Setting up Gmail API credentials..."
    python scripts/setup_gmail.py
}

function Create-Env {
    Write-Info "Creating .env file from template..."
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Success ".env file created from template"
        Write-Warning "Please update .env with your configuration"
    } else {
        Write-Error "env.example not found"
    }
}

function Check-Env {
    Write-Info "Checking environment variables..."
    python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('DATABASE_URL:', os.getenv('DATABASE_URL', 'NOT SET')); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'); print('GMAIL_CREDENTIALS_FILE:', os.getenv('GMAIL_CREDENTIALS_FILE', 'NOT SET'))"
}

function Start-Quick {
    Write-Info "Quick starting Email Ledger POC..."
    Install-Dev
    Create-Env
    Setup-Database
    Write-Success "Quick start complete!"
    Write-Info "Next: .\dev.ps1 run-api or .\dev.ps1 run-cli"
}

function Test-Quick {
    Write-Info "Running quick tests..."
    Format-Check
    Lint-Code
    Test-Package
    Write-Success "Quick test complete!"
}

function Show-Status {
    Write-Info "Project Status"
    Write-Host "=================" -ForegroundColor $Colors.Info
    
    # Python version
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor $Colors.Info
    
    # Package installation
    $packageInfo = pip show email-ledger-poc 2>$null
    if ($packageInfo) {
        $version = ($packageInfo | Select-String "Version:").ToString().Split(":")[1].Trim()
        Write-Host "Package installed: $version" -ForegroundColor $Colors.Success
    } else {
        Write-Host "Package installed: Not installed" -ForegroundColor $Colors.Error
    }
    
    # Environment file
    if (Test-Path ".env") {
        Write-Host "Environment file: Present" -ForegroundColor $Colors.Success
    } else {
        Write-Host "Environment file: Missing" -ForegroundColor $Colors.Error
    }
    
    # Database tables
    try {
        python -c "from src.app.db.models import create_tables; print('Database tables: Ready')" 2>$null
        Write-Host "Database tables: Ready" -ForegroundColor $Colors.Success
    } catch {
        Write-Host "Database tables: Not ready" -ForegroundColor $Colors.Error
    }
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Package }
    "install-dev" { Install-Dev }
    "install-full" { Install-Full }
    "test" { Test-Package }
    "test-cov" { Test-Coverage }
    "lint" { Lint-Code }
    "format" { Format-Code }
    "format-check" { Format-Check }
    "setup" { Setup-Database }
    "demo-data" { Generate-DemoData }
    "clear-data" { Clear-DemoData }
    "run-api" { Start-API }
    "run-api-dev" { Start-APIDev }
    "run-cli" { Start-CLI }
    "run-cli-continuous" { Start-CLIContinuous }
    "run-cli-setup" { Start-CLISetup }
    "docker-build" { Build-Docker }
    "docker-run" { Start-Docker }
    "docker-stop" { Stop-Docker }
    "build" { Build-Package }
    "clean" { Clean-Build }
    "dev-setup" { Setup-Dev }
    "dev-test" { Test-Dev }
    "dev-run" { Start-Dev }
    "setup-gmail" { Setup-Gmail }
    "env-create" { Create-Env }
    "env-check" { Check-Env }
    "quick-start" { Start-Quick }
    "quick-test" { Test-Quick }
    "status" { Show-Status }
    default {
        Write-Error "Unknown command: $Command"
        Write-Info "Use '.\dev.ps1 help' to see available commands"
        exit 1
    }
} 