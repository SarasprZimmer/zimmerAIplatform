# 🚀 Zimmer AI Platform

A comprehensive AI automation platform with user management, payment processing, and admin dashboard.

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (React + TypeScript)
- **Database**: PostgreSQL
- **Authentication**: JWT + OAuth2
- **Payments**: Zarinpal integration
- **Deployment**: Direct server deployment (no Docker)

## 📁 Project Structure

```
zimmer-full-structure/
├── zimmer-backend/           # FastAPI backend
├── zimmer_user_panel/        # User-facing Next.js app
├── zimmermanagement/
│   └── zimmer-admin-dashboard/ # Admin dashboard
├── scripts/                  # Deployment scripts
├── systemd/                  # Systemd service files
├── ops/                     # Operations & testing
└── DEPLOYMENT.md            # Complete deployment guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Nginx

### Local Development

1. **Backend Setup:**
   ```bash
   cd zimmer-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   python main.py
   ```

2. **User Panel:**
   ```bash
   cd zimmer_user_panel
   npm install
   npm run dev
   ```

3. **Admin Dashboard:**
   ```bash
   cd zimmermanagement/zimmer-admin-dashboard
   npm install
   npm run dev
   ```

### Production Deployment

```bash
# Run the automated deployment script
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Features

### User Panel
- User authentication & registration
- AI automation marketplace
- Payment processing
- Usage tracking
- Support tickets
- Settings & security

### Admin Dashboard
- User management
- Automation management
- Payment monitoring
- System analytics
- Backup management
- Knowledge base management

### Backend API
- RESTful API endpoints
- JWT authentication
- Payment processing
- Email notifications
- Database management
- Health monitoring

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [System Architecture](SYSTEM_ARCHITECTURE.md) - Technical architecture details
- [Performance Optimization](PERFORMANCE_OPTIMIZATION_PLAN.md) - Performance guidelines

## 🧪 Testing

```bash
# Run smoke tests
cd ops/smoke
powershell -ExecutionPolicy Bypass -File smoke_backend.ps1
powershell -ExecutionPolicy Bypass -File admin_panel_comprehensive_test.ps1
```

## 🔒 Security

- JWT-based authentication
- CSRF protection
- Input validation
- SQL injection prevention
- Rate limiting
- Secure headers

## 📊 Monitoring

- Health check endpoints
- PM2 process management
- Nginx access logs
- Application metrics
- Error tracking

## 🚀 Deployment

The platform is optimized for direct server deployment without Docker:

- **Better Performance** - No container overhead
- **Easier Debugging** - Direct process access
- **Lower Resource Usage** - More efficient
- **Simpler Management** - Standard Linux processes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation
- Review the logs
- Create an issue in the repository

---

**Status**: ✅ Production Ready
**Last Updated**: January 2025
**Version**: 1.0.0