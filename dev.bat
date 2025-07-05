@echo off
REM Email Ledger POC - Development Scripts (Windows Batch)
REM Usage: dev.bat [command]

setlocal enabledelayedexpansion

if "%1"=="" (
    call :show_help
    exit /b 0
)

if "%1"=="help" (
    call :show_help
    exit /b 0
)

if "%1"=="install" (
    call :install
    exit /b 0
)

if "%1"=="install-dev" (
    call :install_dev
    exit /b 0
)

if "%1"=="test" (
    call :test
    exit /b 0
)

if "%1"=="test-cov" (
    call :test_cov
    exit /b 0
)

if "%1"=="lint" (
    call :lint
    exit /b 0
)

if "%1"=="format" (
    call :format
    exit /b 0
)

if "%1"=="setup" (
    call :setup
    exit /b 0
)

if "%1"=="run-api" (
    call :run_api
    exit /b 0
)

if "%1"=="run-api-dev" (
    call :run_api_dev
    exit /b 0
)

if "%1"=="run-cli" (
    call :run_cli
    exit /b 0
)

if "%1"=="run-cli-continuous" (
    call :run_cli_continuous
    exit /b 0
)

if "%1"=="build" (
    call :build
    exit /b 0
)

if "%1"=="clean" (
    call :clean
    exit /b 0
)

if "%1"=="dev-setup" (
    call :dev_setup
    exit /b 0
)

if "%1"=="env-create" (
    call :env_create
    exit /b 0
)

if "%1"=="status" (
    call :status
    exit /b 0
)

if "%1"=="quick-start" (
    call :quick_start
    exit /b 0
)

echo Unknown command: %1
echo Use 'dev.bat help' to see available commands
exit /b 1

:show_help
echo Email Ledger POC - Development Commands
echo ==========================================
echo.
echo Available commands:
echo   help              Show this help message
echo   install           Install the package in development mode
echo   install-dev       Install with development dependencies
echo   test              Run tests
echo   test-cov          Run tests with coverage
echo   lint              Run linting checks
echo   format            Format code with black and isort
echo   setup             Setup database tables
echo   run-api           Start the API server
echo   run-api-dev       Start API server in development mode
echo   run-cli           Run CLI processor once
echo   run-cli-continuous Run CLI processor continuously
echo   build             Build package for distribution
echo   clean             Clean build artifacts
echo   dev-setup         Complete development setup
echo   env-create        Create .env file from template
echo   status            Show project status
echo   quick-start       Quick start for development
echo.
goto :eof

:install
echo Installing package in development mode...
pip install -e .
if %errorlevel% equ 0 (
    echo Package installed successfully!
) else (
    echo Installation failed!
)
goto :eof

:install_dev
echo Installing with development dependencies...
pip install -e ".[dev,test]"
if %errorlevel% equ 0 (
    echo Development dependencies installed!
) else (
    echo Installation failed!
)
goto :eof

:test
echo Running tests...
python -m pytest tests/ -v
goto :eof

:test_cov
echo Running tests with coverage...
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
goto :eof

:lint
echo Running linting checks...
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
mypy src/ --ignore-missing-imports
goto :eof

:format
echo Formatting code...
black src/ tests/ --line-length=88
isort src/ tests/ --profile=black
echo Code formatted!
goto :eof

:setup
echo Setting up database tables...
python -m src.cli.main setup
goto :eof

:run_api
echo Starting API server...
python -m src.app.api.app
goto :eof

:run_api_dev
echo Starting API server in development mode...
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
uvicorn src.app.api.app:app --reload --host 0.0.0.0 --port 8000
goto :eof

:run_cli
echo Running CLI processor once...
python -m src.cli.main process
goto :eof

:run_cli_continuous
echo Running CLI processor continuously...
python -m src.cli.main process --continuous
goto :eof

:build
echo Building package for distribution...
python build.py
goto :eof

:clean
echo Cleaning build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist htmlcov rmdir /s /q htmlcov
if exist .coverage del .coverage
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"
echo Build artifacts cleaned!
goto :eof

:dev_setup
echo Setting up development environment...
pip install -e ".[dev,test]"
if exist env.example (
    copy env.example .env
    echo .env file created from template
)
echo Development setup complete!
echo Please update .env with your configuration
goto :eof

:env_create
echo Creating .env file from template...
if exist env.example (
    copy env.example .env
    echo .env file created from template
    echo Please update .env with your configuration
) else (
    echo env.example not found
)
goto :eof

:status
echo Project Status
echo =================
python --version
pip show email-ledger-poc 2>nul | findstr Version || echo Package not installed
if exist .env (
    echo Environment file: Present
) else (
    echo Environment file: Missing
)
python -c "from src.app.db.models import create_tables; print('Database tables: Ready')" 2>nul || echo Database tables: Not ready
goto :eof

:quick_start
echo Quick starting Email Ledger POC...
call :install_dev
call :env_create
call :setup
echo Quick start complete!
echo Next: dev.bat run-api or dev.bat run-cli
goto :eof 