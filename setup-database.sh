#!/bin/bash
# Database Setup Script for Zimmer Platform
# This script sets up the PostgreSQL database and runs migrations

set -e  # Exit on any error

echo "🗄️ Setting up Zimmer Platform Database..."

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

# 1. Create database and user
print_status "Creating PostgreSQL database and user..."
sudo -u postgres psql -c "CREATE DATABASE zimmer;" 2>/dev/null || print_warning "Database 'zimmer' may already exist"
sudo -u postgres psql -c "CREATE USER zimmer WITH PASSWORD 'zimmer';" 2>/dev/null || print_warning "User 'zimmer' may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE zimmer TO zimmer;"

print_success "Database and user created"

# 2. Activate virtual environment
print_status "Activating Python virtual environment..."
source venv/bin/activate

# 3. Run database migrations
print_status "Running database migrations..."
cd zimmer-backend
alembic upgrade head

print_success "Database migrations completed"

# 4. Test database connection
print_status "Testing database connection..."
python -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv('env.production')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://zimmer:zimmer@localhost:5432/zimmer')
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection successful!')
"

print_success "Database setup completed successfully!"
echo ""
echo "🗄️ Database Information:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: zimmer"
echo "  User: zimmer"
echo "  Password: zimmer"
echo ""
print_success "Database is ready for the Zimmer Platform! 🚀"
