 # Zimmer Platform - Direct Deployment Guide

This guide covers deploying the Zimmer Platform directly on a server without Docker.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access
- Domain name pointed to your server
- Basic knowledge of Linux command line

## Quick Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/zimmer-platform.git
   cd zimmer-platform
   ```

2. **Run the deployment script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Update configuration:**
   - Edit `/opt/zimmer/zimmer-backend/.env` with your actual values
   - Update domain name in nginx configuration
   - Restart services: `pm2 restart all`

## Manual Deployment Steps

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    postgresql postgresql-contrib nginx curl git build-essential \
    libpq-dev python3-dev

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2
```

### 2. Database Setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE zimmer_production;
CREATE USER zimmer_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE zimmer_production TO zimmer_user;
\q
```

### 3. Application Setup

```bash
# Create app directory
sudo mkdir -p /opt/zimmer
sudo chown $USER:$USER /opt/zimmer

# Clone repository
git clone https://github.com/yourusername/zimmer-platform.git /opt/zimmer
cd /opt/zimmer
```

### 4. Backend Setup

```bash
cd /opt/zimmer/zimmer-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp env.local .env
# Edit .env with your actual values

# Run migrations
alembic upgrade head
```

### 5. Frontend Setup

```bash
# User Panel
cd /opt/zimmer/zimmer_user_panel
npm install
npm run build

# Admin Dashboard
cd /opt/zimmer/zimmermanagement/zimmer-admin-dashboard
npm install
npm run build
```

### 6. Process Management (Choose one)

#### Option A: PM2 (Recommended)

```bash
# Copy ecosystem config
cp ecosystem.config.js.example ecosystem.config.js

# Start services
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Option B: Systemd

```bash
# Copy service files
sudo cp systemd/*.service /etc/systemd/system/

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable zimmer-backend zimmer-user-panel zimmer-admin-dashboard
sudo systemctl start zimmer-backend zimmer-user-panel zimmer-admin-dashboard
```

### 7. Nginx Setup

```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/zimmer

# Enable site
sudo ln -s /etc/nginx/sites-available/zimmer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Setup (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Configuration

### Environment Variables

Edit `/opt/zimmer/zimmer-backend/.env`:

```env
DATABASE_URL=postgresql://zimmer_user:password@localhost:5432/zimmer_production
SECRET_KEY=your-production-secret-key
DEBUG=False
ENVIRONMENT=production
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password
SMTP_FROM=your-email
```

### Nginx Configuration

Update domain name in `/etc/nginx/sites-available/zimmer`:
- Replace `your-domain.com` with your actual domain
- Adjust rate limiting if needed
- Configure SSL if using HTTPS

## Monitoring and Maintenance

### PM2 Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs
pm2 logs zimmer-backend

# Restart services
pm2 restart all
pm2 restart zimmer-backend

# Monitor
pm2 monit
```

### Systemd Commands

```bash
# Check status
sudo systemctl status zimmer-backend

# View logs
sudo journalctl -u zimmer-backend -f

# Restart services
sudo systemctl restart zimmer-backend
```

### Log Locations

- PM2 logs: `/var/log/pm2/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u service-name`

## Troubleshooting

### Common Issues

1. **Backend not starting:**
   - Check database connection
   - Verify environment variables
   - Check logs: `pm2 logs zimmer-backend`

2. **Frontend not loading:**
   - Verify build files exist
   - Check nginx configuration
   - Check nginx logs: `sudo tail -f /var/log/nginx/error.log`

3. **Database connection issues:**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials
   - Test connection: `psql -h localhost -U zimmer_user -d zimmer_production`

### Performance Optimization

1. **Enable gzip compression** (already configured in nginx)
2. **Set up Redis** for caching
3. **Configure CDN** for static assets
4. **Monitor resource usage** with `htop` or `pm2 monit`

## Security Considerations

1. **Firewall setup:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **Regular updates:**
   ```bash
   sudo apt update && sudo apt upgrade
   npm update
   pip list --outdated
   ```

3. **Backup strategy:**
   - Database backups
   - Application code backups
   - Configuration backups

## Backup and Recovery

### Database Backup

```bash
# Create backup
pg_dump -h localhost -U zimmer_user zimmer_production > backup_$(date +%Y%m%d).sql

# Restore backup
psql -h localhost -U zimmer_user zimmer_production < backup_20231201.sql
```

### Application Backup

```bash
# Backup application
tar -czf zimmer_backup_$(date +%Y%m%d).tar.gz /opt/zimmer

# Backup configuration
tar -czf zimmer_config_$(date +%Y%m%d).tar.gz /etc/nginx/sites-available/zimmer /etc/systemd/system/zimmer-*.service
```

## Support

For issues and questions:
- Check logs first
- Review this documentation
- Create an issue in the repository
