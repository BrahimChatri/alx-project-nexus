#!/bin/bash

# Job Board Application Setup Script (Linux/Mac version)
# This script sets up the Django application with Python 3.12, handles errors, and loads fake data

set -e  # Exit on any error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji and formatting
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
STEP="🔄"

# Logging functions
log_success() {
    echo -e "${GREEN}${SUCCESS} $1${NC}"
}

log_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

log_info() {
    echo -e "${CYAN}${INFO} $1${NC}"
}

log_step() {
    echo ""
    echo -e "${BLUE}${STEP} $1${NC}"
    echo -e "${BLUE}==================================================${NC}"
}

# Error handling
handle_error() {
    log_error "$1"
    echo ""
    echo -e "${RED}Setup failed. Please check the error messages above.${NC}"
    exit 1
}

# Parse command line arguments
SKIP_VENV=false
SKIP_MIGRATIONS=false
SKIP_DATA=false
SHOW_HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --skip-data)
            SKIP_DATA=true
            shift
            ;;
        --help|-h)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            SHOW_HELP=true
            shift
            ;;
    esac
done

# Show help
if [ "$SHOW_HELP" = true ]; then
    echo -e "${GREEN}Job Board Application Setup Script${NC}"
    echo -e "${GREEN}==================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage: ./setup_app.sh [options]${NC}"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --skip-venv       Skip virtual environment setup"
    echo "  --skip-migrations Skip database migrations"
    echo "  --skip-data       Skip loading fake data"
    echo "  --help, -h        Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./setup_app.sh                    # Full setup"
    echo "  ./setup_app.sh --skip-data       # Setup without fake data"
    echo "  ./setup_app.sh --skip-venv --skip-data # Quick setup"
    exit 0
fi

# Check if Python 3.12 is available
check_python() {
    log_step "Checking Python 3.12 installation"
    
    PYTHON_CMD=""
    for cmd in python3.12 python3 python; do
        if command -v $cmd &> /dev/null; then
            VERSION=$($cmd --version 2>&1)
            if [[ $VERSION == *"Python 3.12"* ]]; then
                PYTHON_CMD=$cmd
                log_success "Found Python 3.12: $VERSION using command '$cmd'"
                break
            elif [[ $VERSION == *"Python 3."* ]]; then
                PYTHON_CMD=$cmd
                log_warning "Found $VERSION using command '$cmd', but Python 3.12 is recommended"
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        handle_error "Python 3.12 not found. Please install Python 3.12 and ensure it's in your PATH."
    fi
    
    echo $PYTHON_CMD
}

# Setup virtual environment
setup_venv() {
    local python_cmd=$1
    log_step "Setting up virtual environment"
    
    if [ -d "venv" ]; then
        log_info "Virtual environment already exists"
        return
    fi
    
    log_info "Creating virtual environment..."
    $python_cmd -m venv venv || handle_error "Failed to create virtual environment"
    log_success "Virtual environment created successfully"
}

# Activate virtual environment
activate_venv() {
    log_step "Activating virtual environment"
    
    if [ ! -f "venv/bin/activate" ]; then
        handle_error "Virtual environment activation script not found"
    fi
    
    source venv/bin/activate || handle_error "Failed to activate virtual environment"
    log_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    log_step "Installing Python dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt not found, creating basic requirements"
        cat > requirements.txt << EOF
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
django-filter==23.3
drf-yasg==1.21.7
python-decouple==3.8
cryptography==41.0.7
Pillow==10.1.0
faker==20.1.0
EOF
        log_success "Created requirements.txt"
    fi
    
    log_info "Installing dependencies from requirements.txt..."
    python -m pip install --upgrade pip || log_warning "Failed to upgrade pip, continuing..."
    python -m pip install -r requirements.txt || handle_error "Failed to install dependencies"
    log_success "Dependencies installed successfully"
}

# Check Django settings
check_django_settings() {
    log_step "Checking Django configuration"
    
    log_info "Testing Django settings..."
    if python manage.py check --deploy; then
        log_success "Django configuration is valid"
    else
        log_warning "Django configuration has warnings (continuing anyway)"
    fi
}

# Run database migrations
run_migrations() {
    log_step "Running database migrations"
    
    log_info "Making migrations..."
    python manage.py makemigrations || handle_error "Failed to make migrations"
    
    log_info "Applying migrations..."
    python manage.py migrate || handle_error "Failed to apply migrations"
    
    log_success "Database migrations completed successfully"
}

# Load fake data
load_fake_data() {
    log_step "Loading fake data for testing"
    
    if [ ! -f "../tests/load_data.py" ]; then
        log_warning "Fake data script not found at ../tests/load_data.py"
        return
    fi
    
    log_info "Loading fake data (this may take a few minutes)..."
    if python ../tests/load_data.py; then
        log_success "Fake data loaded successfully"
    else
        log_warning "Failed to load fake data, but continuing..."
    fi
}

# Collect static files
collect_static() {
    log_step "Collecting static files"
    
    log_info "Collecting static files..."
    if python manage.py collectstatic --noinput; then
        log_success "Static files collected successfully"
    else
        log_warning "Failed to collect static files, but continuing..."
    fi
}

# Test server startup
test_server() {
    log_step "Testing server startup"
    
    log_info "Testing Django server startup..."
    
    # Start server in background
    python manage.py runserver 8000 --noreload &
    SERVER_PID=$!
    
    # Wait a few seconds for server to start
    sleep 5
    
    # Test if server is responding
    if curl -s http://127.0.0.1:8000/admin/ > /dev/null; then
        log_success "Server started successfully"
    else
        log_warning "Could not connect to server, but it might be running"
    fi
    
    # Kill the test server
    kill $SERVER_PID 2>/dev/null || true
    sleep 2
}

# Show final instructions
show_instructions() {
    echo ""
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo -e "${GREEN}=================${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "${NC}1. Start the development server:${NC}"
    echo -e "${CYAN}   python manage.py runserver${NC}"
    echo ""
    echo -e "${NC}2. Access the application:${NC}"
    echo -e "${CYAN}   • API: http://127.0.0.1:8000/${NC}"
    echo -e "${CYAN}   • Admin: http://127.0.0.1:8000/admin/${NC}"
    echo -e "${CYAN}   • Swagger API Docs: http://127.0.0.1:8000/swagger/${NC}"
    echo ""
    echo -e "${NC}3. Test credentials:${NC}"
    echo -e "${CYAN}   • Admin: username=admin, password=admin123${NC}"
    echo -e "${CYAN}   • Test user: username=johnsmith1, password=password123${NC}"
    echo ""
    echo -e "${NC}4. Useful commands:${NC}"
    echo -e "${CYAN}   • Create superuser: python manage.py createsuperuser${NC}"
    echo -e "${CYAN}   • Run tests: python manage.py test${NC}"
    echo -e "${CYAN}   • Shell: python manage.py shell${NC}"
    echo ""
}

# Main function
main() {
    echo ""
    echo -e "${GREEN}🚀 Job Board Application Setup${NC}"
    echo -e "${GREEN}==============================${NC}"
    echo ""
    
    # Change to backend directory
    SCRIPT_DIR="$(dirname "$0")"
    BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"
    if [ -d "$BACKEND_DIR" ]; then
        cd "$BACKEND_DIR"
        log_info "Working directory: $(pwd)"
    else
        handle_error "Backend directory not found at $BACKEND_DIR"
    fi
    
    # Step 1: Check Python
    PYTHON_CMD=$(check_python)
    
    # Step 2: Setup virtual environment (unless skipped)
    if [ "$SKIP_VENV" = false ]; then
        setup_venv $PYTHON_CMD
        activate_venv
        install_dependencies
    else
        log_warning "Skipping virtual environment setup"
        # Still try to activate if it exists
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
    fi
    
    # Step 3: Check Django settings
    check_django_settings
    
    # Step 4: Run migrations (unless skipped)
    if [ "$SKIP_MIGRATIONS" = false ]; then
        run_migrations
    else
        log_warning "Skipping database migrations"
    fi
    
    # Step 5: Collect static files
    collect_static
    
    # Step 6: Load fake data (unless skipped)
    if [ "$SKIP_DATA" = false ]; then
        load_fake_data
    else
        log_warning "Skipping fake data loading"
    fi
    
    # Step 7: Test server startup
    test_server
    
    # Step 8: Show final instructions
    show_instructions
}

# Run main function
main "$@"
