#!/bin/bash
# Service Management Script for Zimmer Platform
# This script provides easy management of all services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Zimmer Platform Service Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  health    - Check service health"
    echo "  backup    - Backup database"
    echo "  update    - Update from repository"
    echo ""
}

# Function to start services
start_services() {
    print_status "Starting all Zimmer Platform services..."
    pm2 start ecosystem.config.js
    print_success "All services started"
}

# Function to stop services
stop_services() {
    print_status "Stopping all Zimmer Platform services..."
    pm2 stop all
    print_success "All services stopped"
}

# Function to restart services
restart_services() {
    print_status "Restarting all Zimmer Platform services..."
    pm2 restart all
    print_success "All services restarted"
}

# Function to show status
show_status() {
    print_status "Zimmer Platform Service Status:"
    echo ""
    pm2 status
    echo ""
    print_status "Service URLs:"
    echo "  🔧 Backend API: http://localhost:8000"
    echo "  👤 User Panel: http://localhost:3000"
    echo "  🎛️ Admin Dashboard: http://localhost:4000"
}

# Function to show logs
show_logs() {
    print_status "Showing service logs (Press Ctrl+C to exit)..."
    pm2 logs
}

# Function to check health
check_health() {
    print_status "Checking service health..."
    echo ""
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "✅ Backend API is healthy"
    else
        print_error "❌ Backend API is not responding"
    fi
    
    # Check user panel
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "✅ User Panel is healthy"
    else
        print_error "❌ User Panel is not responding"
    fi
    
    # Check admin dashboard
    if curl -s http://localhost:4000 > /dev/null; then
        print_success "✅ Admin Dashboard is healthy"
    else
        print_error "❌ Admin Dashboard is not responding"
    fi
    
    # Check database
    if psql -h localhost -U zimmer -d zimmer -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "✅ Database is healthy"
    else
        print_error "❌ Database connection failed"
    fi
}

# Function to backup database
backup_database() {
    print_status "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    pg_dump -h localhost -U zimmer zimmer > "backups/$BACKUP_FILE"
    print_success "Database backed up to: backups/$BACKUP_FILE"
}

# Function to update from repository
update_services() {
    print_status "Updating from repository..."
    git pull origin main
    
    print_status "Rebuilding frontend applications..."
    cd zimmer_user_panel
    npm run build
    cd ../zimmermanagement/zimmer-admin-dashboard
    npm run build
    cd ../..
    
    print_status "Restarting services..."
    pm2 restart all
    
    print_success "Services updated and restarted"
}

# Main script logic
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    backup)
        backup_database
        ;;
    update)
        update_services
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
