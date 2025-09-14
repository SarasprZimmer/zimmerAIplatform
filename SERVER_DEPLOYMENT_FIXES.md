# 🚨 SERVER DEPLOYMENT ISSUES & FIXES

## **CRITICAL ISSUES IDENTIFIED**

### **1. BACKEND CONFIGURATION FIXES**

#### **Fix Database URL:**
```bash
# ❌ CURRENT (WRONG):
DATABASE_URL=postgresql+psycopg2://zimmer:zimmer@postgres:5432/zimmer

# ✅ CORRECT for direct deployment:
DATABASE_URL=postgresql+psycopg2://zimmer:zimmer@localhost:5432/zimmer
```

#### **Add Missing Dependencies to requirements.txt:**
```txt
# Add these missing packages:
redis==5.0.1
psycopg2-binary==2.9.9
# (Already present, but verify versions)
```

### **2. SYSTEM DEPENDENCIES (Ubuntu/Debian Server)**

```bash
# Install essential packages
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    nodejs \
    npm \
    build-essential \
    libpq-dev \
    git

# Install PM2 globally
sudo npm install -g pm2
```

### **3. DATABASE SETUP**

```sql
-- Connect to PostgreSQL as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE zimmer;
CREATE USER zimmer WITH PASSWORD 'zimmer';
GRANT ALL PRIVILEGES ON DATABASE zimmer TO zimmer;
\q
```

### **4. PM2 CONFIGURATION FIXES**

#### **Update ecosystem.config.js for Linux:**
```javascript
module.exports = {
  apps: [
    {
      name: 'zimmer-backend',
      script: 'zimmer-backend/main.py',
      interpreter: './venv/bin/python',  // ✅ Linux path
      cwd: '/opt/zimmer/zimmer-platform-final',  // ✅ Absolute path
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true
    },
    {
      name: 'zimmer-user-panel',
      script: 'npm',
      args: 'start',
      cwd: '/opt/zimmer/zimmer-platform-final/zimmer_user_panel',  // ✅ Absolute path
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/user-panel-error.log',
      out_file: './logs/user-panel-out.log',
      log_file: './logs/user-panel-combined.log',
      time: true,
      kill_timeout: 5000
    },
    {
      name: 'zimmer-admin-dashboard',
      script: 'npm',
      args: 'start',
      cwd: '/opt/zimmer/zimmer-platform-final/zimmermanagement/zimmer-admin-dashboard',  // ✅ Absolute path
      env: {
        NODE_ENV: 'production',
        PORT: 4000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/admin-dashboard-error.log',
      out_file: './logs/admin-dashboard-out.log',
      log_file: './logs/admin-dashboard-combined.log',
      time: true,
      kill_timeout: 5000
    }
  ]
};
```

### **5. FRONTEND ENVIRONMENT FILES**

#### **Create zimmer_user_panel/.env.production:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

#### **Create zimmermanagement/zimmer-admin-dashboard/.env.production:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

### **6. DEPLOYMENT SCRIPT FOR SERVER**

```bash
#!/bin/bash
# deploy-server.sh

echo "🚀 Starting Zimmer Platform Server Deployment..."

# 1. Update system packages
sudo apt-get update

# 2. Install system dependencies
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev postgresql postgresql-contrib redis-server nginx nodejs npm build-essential libpq-dev git

# 3. Install PM2
sudo npm install -g pm2

# 4. Setup PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE zimmer;"
sudo -u postgres psql -c "CREATE USER zimmer WITH PASSWORD 'zimmer';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE zimmer TO zimmer;"

# 5. Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 6. Create project directory
sudo mkdir -p /opt/zimmer
sudo chown $USER:$USER /opt/zimmer

# 7. Clone repository
cd /opt/zimmer
git clone https://github.com/SarasprZimmer/zimmer-platform-final.git
cd zimmer-platform-final

# 8. Setup Python virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r zimmer-backend/requirements.txt

# 9. Setup frontend applications
cd zimmer_user_panel
npm install
npm run build
cd ../zimmermanagement/zimmer-admin-dashboard
npm install
npm run build
cd ../..

# 10. Create logs directory
mkdir -p logs

# 11. Start services with PM2
pm2 start ecosystem.config.js

# 12. Save PM2 configuration
pm2 save
pm2 startup

echo "✅ Deployment completed!"
echo "🌐 Services running on:"
echo "  Backend: http://localhost:8000"
echo "  User Panel: http://localhost:3000"
echo "  Admin Dashboard: http://localhost:4000"
```

### **7. VERIFICATION COMMANDS**

```bash
# Check PM2 status
pm2 status

# Check logs
pm2 logs

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:4000

# Check database connection
psql -h localhost -U zimmer -d zimmer -c "SELECT 1;"
```

## **SUMMARY OF FIXES NEEDED:**

1. ✅ **Database URL**: Change from `postgres:5432` to `localhost:5432`
2. ✅ **PM2 Paths**: Use absolute Linux paths instead of relative Windows paths
3. ✅ **System Dependencies**: Install PostgreSQL, Redis, Python 3.11, Node.js
4. ✅ **Environment Files**: Create production environment files for frontend
5. ✅ **Database Setup**: Create database and user in PostgreSQL
6. ✅ **Permissions**: Ensure proper file permissions
7. ✅ **Service Management**: Use PM2 for process management

These fixes address all the configuration issues that would cause deployment failures on the server.
