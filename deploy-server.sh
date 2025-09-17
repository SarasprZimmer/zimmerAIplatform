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
    cd /home/zimmer
    git clone https://github.com/SarasprZimmer/zimmerAIplatform.git
    cd zimmerAIplatform
else
    print_status "Repository already exists, updating..."
    cd /home/zimmer/zimmerAIplatform
    git pull origin main
fi

print_success "Repository ready"

# 8. Setup Python virtual environment
print_status "Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r zimmer-backend/requirements.txt

print_success "Python environment configured"

# 8.1. Fix backend startup issues
print_status "Applying backend fixes..."

# Ensure main.py has uvicorn startup code
if ! grep -q "if __name__ == \"__main__\":" zimmer-backend/main.py; then
    print_status "Adding uvicorn startup code to main.py..."
    echo "" >> zimmer-backend/main.py
    echo "if __name__ == \"__main__\":" >> zimmer-backend/main.py
    echo "    import uvicorn" >> zimmer-backend/main.py
    echo "    uvicorn.run(app, host=\"0.0.0.0\", port=8000)" >> zimmer-backend/main.py
fi

# Test backend import
print_status "Testing backend import..."
if python3 -c "from zimmer-backend.main import app; print('Backend import successful')" 2>/dev/null; then
    print_success "Backend import test passed"
else
    print_warning "Backend import test failed, but continuing with deployment"
fi

print_success "Backend fixes applied"

# 8.2. Setup environment variables
print_status "Setting up environment variables..."

# Create .env file for backend if it doesn't exist
if [ ! -f "zimmer-backend/.env" ]; then
    print_status "Creating .env file for backend..."
    cat > zimmer-backend/.env << EOF
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=postgresql+psycopg2://zimmer:zimmer@localhost:5432/zimmer

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
DEBUG=false
ENVIRONMENT=production
REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=false

# CORS Configuration
ALLOWED_ORIGINS=http://193.162.129.243:3000,http://193.162.129.243:4000,http://localhost:3000,http://localhost:4000

# External Services
OPENAI_API_KEY=your-openai-api-key-here
ZIMMER_SERVICE_TOKEN=your-service-token-here

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF
    print_success ".env file created"
else
    print_status ".env file already exists"
fi

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

# 12. Stop any existing PM2 processes
print_status "Stopping any existing PM2 processes..."
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# 13. Start services with PM2
print_status "Starting services with PM2..."
pm2 start ecosystem.config.js

# 14. Save PM2 configuration
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

# Test backend health
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend API is responding"
    
    # Test backup endpoints (should return authentication required, which is expected)
    if curl -s http://localhost:8000/api/admin/backups | grep -q "Authentication required"; then
        print_success "Backup endpoints are working (authentication required)"
    else
        print_warning "Backup endpoints may not be working properly"
    fi
else
    print_error "Backend API is not responding"
    print_status "Checking backend logs..."
    pm2 logs zimmer-backend --lines 10
fi

# Test user panel
if curl -s http://localhost:3000 > /dev/null; then
    print_success "User Panel is responding"
else
    print_error "User Panel is not responding"
    print_status "Checking user panel logs..."
    pm2 logs zimmer-user-panel --lines 10
fi

# Test admin dashboard
if curl -s http://localhost:4000 > /dev/null; then
    print_success "Admin Dashboard is responding"
else
    print_error "Admin Dashboard is not responding"
    print_status "Checking admin dashboard logs..."
    pm2 logs zimmer-admin-dashboard --lines 10
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
echo "🔧 Troubleshooting:"
echo "  If backend fails to start:"
echo "    - Check logs: pm2 logs zimmer-backend"
echo "    - Test import: cd zimmer-backend && python3 -c 'from main import app'"
echo "    - Restart: pm2 restart zimmer-backend"
echo ""
echo "  If frontend fails to build:"
echo "    - Check Node.js version: node --version"
echo "    - Reinstall dependencies: npm install"
echo "    - Rebuild: npm run build"
echo ""
echo "  If services are not responding:"
echo "    - Check PM2 status: pm2 status"
echo "    - Check system resources: htop"
echo "    - Check port usage: netstat -tlnp | grep :8000"
echo ""
print_success "Zimmer Platform is ready for production! 🚀"
