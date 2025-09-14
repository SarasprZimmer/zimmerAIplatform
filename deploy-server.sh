#!/bin/bash
# Zimmer Platform Server Deployment Script
# This script deploys the Zimmer platform to a Linux server

set -e  # Exit on any error

echo "🚀 Starting Zimmer Platform Server Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# 1. Update system packages
print_status "Updating system packages..."
sudo apt-get update

# 2. Install system dependencies
print_status "Installing system dependencies..."
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    nodejs \
    build-essential \
    libpq-dev \
    git \
    curl \
    wget

print_success "System dependencies installed"

# 3. Install PM2 globally
print_status "Installing PM2 process manager..."
sudo npm install -g pm2

print_success "PM2 installed"

# 4. Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE zimmer;" 2>/dev/null || print_warning "Database 'zimmer' may already exist"
sudo -u postgres psql -c "CREATE USER zimmer WITH PASSWORD 'zimmer';" 2>/dev/null || print_warning "User 'zimmer' may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE zimmer TO zimmer;"

print_success "PostgreSQL database configured"

# 5. Start and enable Redis
print_status "Starting Redis server..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

print_success "Redis server started and enabled"

# 6. Create project directory
print_status "Setting up project directory..."
sudo mkdir -p /opt/zimmer
sudo chown $USER:$USER /opt/zimmer

# 7. Clone repository (if not already present)
if [ ! -d "/home/zimmer/zimmerAIplatform" ]; then
    print_status "Cloning repository..."
    cd /opt/zimmer
    # git clone https://github.com/SarasprZimmer/zimmer-platform-final.git
else
    print_status "Repository already exists, updating..."
    cd /home/zimmer/zimmerAIplatform
    git pull origin main
fi

cd /home/zimmer/zimmerAIplatform

print_success "Repository ready"

# 8. Setup Python virtual environment
print_status "Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r zimmer-backend/requirements.txt

print_success "Python environment configured"

# 9. Setup frontend applications
print_status "Setting up frontend applications..."

# User Panel
print_status "Installing user panel dependencies..."
cd zimmer_user_panel
npm install
npm run build
cd ..

# Admin Dashboard
print_status "Installing admin dashboard dependencies..."
cd zimmermanagement/zimmer-admin-dashboard
npm install
npm run build
cd ../..

print_success "Frontend applications built"

# 10. Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# 11. Set proper permissions
print_status "Setting file permissions..."
chmod +x ecosystem.config.js
chmod +x deploy-server.sh

# 12. Start services with PM2
print_status "Starting services with PM2..."
pm2 start ecosystem.config.js

# 13. Save PM2 configuration
print_status "Saving PM2 configuration..."
pm2 save
pm2 startup

print_success "PM2 configuration saved"

# 14. Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# 15. Verify services are running
print_status "Verifying services..."

# Check PM2 status
pm2 status

# Test endpoints
print_status "Testing service endpoints..."

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend API is responding"
else
    print_error "Backend API is not responding"
fi

# Test user panel
if curl -s http://localhost:3000 > /dev/null; then
    print_success "User Panel is responding"
else
    print_error "User Panel is not responding"
fi

# Test admin dashboard
if curl -s http://localhost:4000 > /dev/null; then
    print_success "Admin Dashboard is responding"
else
    print_error "Admin Dashboard is not responding"
fi

# Test database connection
if psql -h localhost -U zimmer -d zimmer -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection is working"
else
    print_error "Database connection failed"
fi

echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Services are now running:"
echo "  🔧 Backend API: http://localhost:8000"
echo "  👤 User Panel: http://localhost:3000"
echo "  🎛️ Admin Dashboard: http://localhost:4000"
echo ""
echo "📝 Useful commands:"
echo "  pm2 status          - Check service status"
echo "  pm2 logs            - View all logs"
echo "  pm2 logs [app-name] - View specific app logs"
echo "  pm2 restart all     - Restart all services"
echo "  pm2 stop all        - Stop all services"
echo ""
print_success "Zimmer Platform is ready for production! 🚀"
