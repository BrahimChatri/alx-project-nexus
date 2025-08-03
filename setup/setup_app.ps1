# Job Board Application Setup Script
# This script sets up the Django application with Python 3.12, handles errors, and loads fake data

param(
    [switch]$SkipVenv,
    [switch]$SkipMigrations,
    [switch]$SkipData,
    [switch]$Help
)

# Show help
if ($Help) {
    Write-Host "Job Board Application Setup Script" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\setup_app.ps1 [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -SkipVenv       Skip virtual environment setup"
    Write-Host "  -SkipMigrations Skip database migrations"
    Write-Host "  -SkipData       Skip loading fake data"
    Write-Host "  -Help           Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\setup_app.ps1                    # Full setup"
    Write-Host "  .\setup_app.ps1 -SkipData          # Setup without fake data"
    Write-Host "  .\setup_app.ps1 -SkipVenv -SkipData # Quick setup"
    exit 0
}

# Color functions
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "🔄 $Message" -ForegroundColor Blue
    Write-Host "=" * 50 -ForegroundColor Blue
}

# Error handling function
function Handle-Error {
    param([string]$ErrorMessage, [int]$ExitCode = 1)
    Write-Error $ErrorMessage
    Write-Host ""
    Write-Host "Setup failed. Please check the error messages above." -ForegroundColor Red
    exit $ExitCode
}

# Check if Python 3.12 is available
function Test-Python312 {
    Write-Step "Checking Python 3.12 installation"
    
    $pythonCommands = @("python3.12", "python", "py")
    $pythonFound = $false
    $pythonCmd = ""
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -match "Python 3\.12") {
                $pythonFound = $true
                $pythonCmd = $cmd
                Write-Success "Found Python 3.12: $version using command '$cmd'"
                break
            } elseif ($version -match "Python 3\.") {
                Write-Warning "Found $version using command '$cmd', but Python 3.12 is recommended"
                $pythonCmd = $cmd
            }
        } catch {
            # Command not found, continue
        }
    }
    
    if (-not $pythonFound -and $pythonCmd) {
        Write-Warning "Python 3.12 not found, but using $pythonCmd"
        $pythonFound = $true
    }
    
    if (-not $pythonFound) {
        Handle-Error "Python 3.12 not found. Please install Python 3.12 and ensure it's in your PATH."
    }
    
    return $pythonCmd
}

# Setup virtual environment
function Setup-VirtualEnvironment {
    param([string]$PythonCmd)
    
    Write-Step "Setting up virtual environment"
    
    if (Test-Path "venv") {
        Write-Info "Virtual environment already exists"
        return
    }
    
    try {
        Write-Info "Creating virtual environment..."
        & $PythonCmd -m venv venv
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to create virtual environment"
        }
        Write-Success "Virtual environment created successfully"
    } catch {
        Handle-Error "Error creating virtual environment: $($_.Exception.Message)"
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    Write-Step "Activating virtual environment"
    
    $activateScript = "venv\Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Handle-Error "Virtual environment activation script not found at $activateScript"
    }
    
    try {
        & $activateScript
        Write-Success "Virtual environment activated"
    } catch {
        Handle-Error "Failed to activate virtual environment: $($_.Exception.Message)"
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Step "Installing Python dependencies"
    
    if (-not (Test-Path "requirements.txt")) {
        Write-Warning "requirements.txt not found, creating basic requirements"
        $requirements = @(
            "Django==4.2.7",
            "djangorestframework==3.14.0",
            "djangorestframework-simplejwt==5.3.0",
            "django-cors-headers==4.3.1",
            "django-filter==23.3",
            "drf-yasg==1.21.7",
            "python-decouple==3.8",
            "cryptography==41.0.7",
            "Pillow==10.1.0",
            "faker==20.1.0"
        )
        $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
        Write-Success "Created requirements.txt"
    }
    
    try {
        Write-Info "Installing dependencies from requirements.txt..."
        python -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to upgrade pip, continuing..."
        }
        
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to install dependencies"
        }
        Write-Success "Dependencies installed successfully"
    } catch {
        Handle-Error "Error installing dependencies: $($_.Exception.Message)"
    }
}

# Check Django settings
function Test-DjangoSettings {
    Write-Step "Checking Django configuration"
    
    try {
        Write-Info "Testing Django settings..."
        python manage.py check --deploy
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Django configuration is valid"
        } else {
            Write-Warning "Django configuration has warnings (continuing anyway)"
        }
    } catch {
        Write-Warning "Could not validate Django settings: $($_.Exception.Message)"
    }
}

# Run database migrations
function Run-Migrations {
    Write-Step "Running database migrations"
    
    try {
        Write-Info "Making migrations..."
        python manage.py makemigrations
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to make migrations"
        }
        
        Write-Info "Applying migrations..."
        python manage.py migrate
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to apply migrations"
        }
        
        Write-Success "Database migrations completed successfully"
    } catch {
        Handle-Error "Error running migrations: $($_.Exception.Message)"
    }
}

# Load fake data
function Load-FakeData {
    Write-Step "Loading fake data for testing"
    
    $dataScript = "..\tests\load_data.py"
    if (-not (Test-Path $dataScript)) {
        Write-Warning "Fake data script not found at $dataScript"
        return
    }
    
    try {
        Write-Info "Loading fake data (this may take a few minutes)..."
        python $dataScript
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to load fake data, but continuing..."
        } else {
            Write-Success "Fake data loaded successfully"
        }
    } catch {
        Write-Warning "Error loading fake data: $($_.Exception.Message)"
    }
}

# Collect static files
function Collect-StaticFiles {
    Write-Step "Collecting static files"
    
    try {
        Write-Info "Collecting static files..."
        python manage.py collectstatic --noinput
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to collect static files, but continuing..."
        } else {
            Write-Success "Static files collected successfully"
        }
    } catch {
        Write-Warning "Error collecting static files: $($_.Exception.Message)"
    }
}

# Test server startup
function Test-ServerStartup {
    Write-Step "Testing server startup"
    
    try {
        Write-Info "Testing Django server startup..."
        $job = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            python manage.py runserver 8000 --noreload
        }
        
        Start-Sleep -Seconds 5
        
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/admin/" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 302) {
                Write-Success "Server started successfully"
            }
        } catch {
            Write-Warning "Could not connect to server, but it might be running"
        }
        
        Stop-Job $job
        Remove-Job $job
        
    } catch {
        Write-Warning "Could not test server startup: $($_.Exception.Message)"
    }
}

# Show final instructions
function Show-Instructions {
    Write-Host ""
    Write-Host "🎉 Setup Complete!" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Start the development server:" -ForegroundColor White
    Write-Host "   python manage.py runserver" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Access the application:" -ForegroundColor White
    Write-Host "   • API: http://127.0.0.1:8000/" -ForegroundColor Cyan
    Write-Host "   • Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Cyan
    Write-Host "   • Swagger API Docs: http://127.0.0.1:8000/swagger/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Test credentials:" -ForegroundColor White
    Write-Host "   • Admin: username=admin, password=admin123" -ForegroundColor Cyan
    Write-Host "   • Test user: username=johnsmith1, password=password123" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Useful commands:" -ForegroundColor White
    Write-Host "   • Create superuser: python manage.py createsuperuser" -ForegroundColor Cyan
    Write-Host "   • Run tests: python manage.py test" -ForegroundColor Cyan
    Write-Host "   • Shell: python manage.py shell" -ForegroundColor Cyan
    Write-Host ""
}

# Main setup function
function Main {
    Write-Host ""
    Write-Host "🚀 Job Board Application Setup" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host ""
    
    # Change to backend directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $backendDir = Join-Path (Split-Path $scriptDir -Parent) "backend"
    if (Test-Path $backendDir) {
        Set-Location $backendDir
        Write-Info "Working directory: $(Get-Location)"
    } else {
        Handle-Error "Backend directory not found at $backendDir"
    }
    
    try {
        # Step 1: Check Python
        $pythonCmd = Test-Python312
        
        # Step 2: Setup virtual environment (unless skipped)
        if (-not $SkipVenv) {
            Setup-VirtualEnvironment -PythonCmd $pythonCmd
            Enable-VirtualEnvironment
            Install-Dependencies
        } else {
            Write-Warning "Skipping virtual environment setup"
        }
        
        # Step 3: Check Django settings
        Test-DjangoSettings
        
        # Step 4: Run migrations (unless skipped)
        if (-not $SkipMigrations) {
            Run-Migrations
        } else {
            Write-Warning "Skipping database migrations"
        }
        
        # Step 5: Collect static files
        Collect-StaticFiles
        
        # Step 6: Load fake data (unless skipped)
        if (-not $SkipData) {
            Load-FakeData
        } else {
            Write-Warning "Skipping fake data loading"
        }
        
        # Step 7: Test server startup
        Test-ServerStartup
        
        # Step 8: Show final instructions
        Show-Instructions
        
    } catch {
        Handle-Error "Unexpected error during setup: $($_.Exception.Message)"
    }
}

# Run main function
Main
