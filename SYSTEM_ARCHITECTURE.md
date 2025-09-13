# 🏗️ Zimmer AI Platform - System Architecture

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  🌐 User Panel (Next.js)    │  🛠️ Admin Dashboard (Next.js)   │
│  - React 18 + TypeScript    │  - React 18 + TypeScript        │
│  - Tailwind CSS             │  - Tailwind CSS                 │
│  - Persian Language         │  - English Language             │
│  - Port: 3000               │  - Port: 3001                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  🔀 Nginx Reverse Proxy                                        │
│  - SSL Termination                                            │
│  - Load Balancing                                             │
│  - Static File Serving                                        │
│  - Rate Limiting                                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  🚀 FastAPI Backend (Python 3.9+)                             │
│  - RESTful API                                                │
│  - JWT Authentication                                         │
│  - CORS Support                                               │
│  - Port: 8000                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ PostgreSQL Database                                        │
│  - User Management                                            │
│  - Automation Data                                            │
│  - Payment Records                                            │
│  - Support Tickets                                            │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Details

### **Frontend Applications**

#### **User Panel** (`zimmer_user_panel/`)
```
📁 zimmer_user_panel/
├── 📄 pages/
│   ├── 🏠 index.tsx (Dashboard)
│   ├── 🔐 login.tsx
│   ├── 📝 signup.tsx
│   ├── 🛒 automations/
│   │   ├── marketplace.tsx
│   │   └── [id]/
│   │       ├── index.tsx
│   │       ├── dashboard.tsx
│   │       └── tokens.tsx
│   ├── 🎫 support.tsx
│   └── ⚙️ settings.tsx
├── 📁 components/
│   ├── 🎨 dashboard/ (Charts & Stats)
│   ├── 🤖 automations/
│   ├── 💳 payments/
│   └── 🔔 notifications/
├── 📁 lib/
│   ├── 🔌 apiClient.ts
│   ├── 🔐 authClient.ts
│   └── 🛠️ api.ts
└── 📁 contexts/
    └── 🔐 AuthContext.tsx
```

#### **Admin Dashboard** (`zimmermanagement/zimmer-admin-dashboard/`)
```
📁 zimmer-admin-dashboard/
├── 📄 pages/
│   ├── 🏠 index.tsx (Admin Dashboard)
│   ├── 👥 users.tsx
│   ├── 🤖 user-automations.tsx
│   ├── 🔑 api-keys.tsx
│   └── 📊 analytics.tsx
├── 📁 components/
│   ├── 📊 charts/
│   ├── 📋 tables/
│   └── 🎛️ forms/
└── 📁 lib/
    ├── 🔌 api.ts
    └── 🔐 auth-client.ts
```

### **Backend API** (`zimmer-backend/`)

```
📁 zimmer-backend/
├── 📄 main.py (FastAPI App)
├── 📁 routers/
│   ├── 🔐 auth.py (Authentication)
│   ├── 👥 users.py (User Management)
│   ├── 🤖 automations.py (Automation Marketplace)
│   ├── 💳 payments.py (Payment Processing)
│   ├── 🎫 support.py (Support System)
│   └── 📁 admin/
│       ├── __init__.py (Admin Dashboard API)
│       ├── user_management.py
│       ├── openai_keys.py
│       └── token_adjustments.py
├── 📁 models/
│   ├── 👤 user.py
│   ├── 🤖 automation.py
│   ├── 🔗 user_automation.py
│   ├── 💳 payment.py
│   └── 🎫 ticket.py
├── 📁 schemas/
│   ├── 👤 user_schemas.py
│   ├── 🤖 automation_schemas.py
│   └── 💳 payment_schemas.py
├── 📁 utils/
│   ├── 🔐 auth.py
│   ├── 🔑 jwt.py
│   └── 💰 zarinpal.py
└── 📄 database.py
```

## 🗄️ Database Schema

### **Core Tables**

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email_verified_at TIMESTAMP,
    twofa_enabled BOOLEAN DEFAULT FALSE,
    twofa_secret VARCHAR(64)
);

-- Automations Table
CREATE TABLE automations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    pricing_type VARCHAR(50) DEFAULT 'token_per_session',
    price_per_token DECIMAL(10,2),
    status BOOLEAN DEFAULT TRUE,
    is_listed BOOLEAN DEFAULT TRUE,
    health_status VARCHAR(50) DEFAULT 'healthy',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Automations Table
CREATE TABLE user_automations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    automation_id INTEGER REFERENCES automations(id),
    telegram_bot_token VARCHAR(255),
    tokens_remaining INTEGER DEFAULT 5,
    demo_tokens INTEGER DEFAULT 5,
    is_demo_active BOOLEAN DEFAULT TRUE,
    demo_expired BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'active',
    provisioned_at TIMESTAMP WITH TIME ZONE,
    integration_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments Table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    automation_id INTEGER REFERENCES automations(id),
    amount DECIMAL(10,2) NOT NULL,
    tokens_purchased INTEGER NOT NULL,
    method VARCHAR(50) DEFAULT 'zarinpal',
    gateway VARCHAR(50) DEFAULT 'zarinpal',
    transaction_id VARCHAR(255) UNIQUE,
    authority VARCHAR(255),
    ref_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    discount_code VARCHAR(50),
    discount_percent DECIMAL(5,2),
    meta TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Support Tickets Table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(50) DEFAULT 'medium',
    importance VARCHAR(50) DEFAULT 'normal',
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔄 Data Flow

### **User Registration Flow**
```
1. User fills registration form
2. Frontend sends POST /api/auth/register
3. Backend validates data and creates user
4. JWT token generated and returned
5. Frontend stores token in localStorage
6. User redirected to dashboard
```

### **Automation Purchase Flow**
```
1. User browses marketplace
2. Frontend calls GET /api/automations/available
3. User selects automation and clicks "Add"
4. Frontend calls POST /api/user/automations/{id}
5. Backend creates UserAutomation record with 5 free tokens
6. User redirected to automations page
```

### **Token Purchase Flow**
```
1. User clicks "Buy Tokens" on automation
2. Frontend calls POST /api/payments/zarinpal/init
3. Backend creates payment record and calls Zarinpal API
4. User redirected to Zarinpal payment page
5. After payment, Zarinpal redirects to callback URL
6. Backend verifies payment and credits tokens
7. User redirected to success page
```

### **Admin Dashboard Flow**
```
1. Admin logs in with manager/technical/support role
2. Frontend calls GET /api/admin/dashboard/stats
3. Backend queries database for statistics
4. Frontend displays charts and metrics
5. Admin can manage users, view automations, etc.
```

## 🔒 Security Architecture

### **Authentication & Authorization**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│                 │    │                 │    │                 │
│ 1. Login Form   │───▶│ 2. Validate     │───▶│ 3. Check User   │
│                 │    │    Credentials  │    │    Credentials  │
│                 │◀───│ 4. Generate JWT │◀───│ 5. Return User  │
│ 6. Store Token  │    │    Token        │    │    Data         │
│                 │    │                 │    │                 │
│ 7. API Calls    │───▶│ 8. Verify JWT   │───▶│ 9. Check        │
│    with Token   │    │    Token        │    │    Permissions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Role-Based Access Control**
```
👑 Manager Role:
   - Full system access
   - User management
   - Payment monitoring
   - System configuration

🛠️ Technical Team Role:
   - User management
   - Automation management
   - API key management
   - System monitoring

🎧 Support Staff Role:
   - User management
   - Support ticket handling
   - Basic analytics

👤 Customer Role:
   - Own profile management
   - Automation marketplace
   - Token purchases
   - Support tickets
```

## 📊 Performance Architecture

### **Caching Strategy**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Nginx         │    │   Backend       │
│                 │    │                 │    │                 │
│ - Browser Cache │    │ - Static Files  │    │ - Redis Cache   │
│ - Local Storage │    │ - API Responses │    │ - Session Data  │
│ - Service Worker│    │ - Gzip Compression│   │ - Query Results │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Database Optimization**
```sql
-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_user_automations_user_id ON user_automations(user_id);
CREATE INDEX idx_user_automations_automation_id ON user_automations(automation_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
```

## 🚀 Deployment Architecture

### **Production Environment**
```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER (Nginx)                       │
│  - SSL Termination                                            │
│  - Static File Serving                                        │
│  - Load Balancing                                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  User Panel     │  │  Admin Dashboard│  │  API Backend    │
│  (Port 3000)    │  │  (Port 3001)    │  │  (Port 8000)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                       │
│  - Primary Database                                            │
│  - Read Replicas (Optional)                                   │
│  - Automated Backups                                          │
└─────────────────────────────────────────────────────────────────┘
```

### **Monitoring & Logging**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PM2 Process   │    │   Nginx Logs    │    │   Application   │
│   Manager       │    │   - Access Log  │    │   Logs          │
│   - Process     │    │   - Error Log   │    │   - API Calls   │
│     Monitoring  │    │   - SSL Log     │    │   - Errors      │
│   - Auto        │    │                 │    │   - Performance │
│     Restart     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration Management

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/zimmer_platform
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zimmer_platform
DB_USER=zimmer_user
DB_PASSWORD=secure_password

# JWT
JWT_SECRET_KEY=your_super_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# API URLs
API_BASE_URL=https://api.zimmerai.com
FRONTEND_URL=https://zimmerai.com
ADMIN_URL=https://admin.zimmerai.com

# Payment
ZARRINPAL_MERCHANT_ID=your_merchant_id
ZARRINPAL_BASE_URL=https://api.zarinpal.com/pg/rest/WebGate
PAYMENTS_MODE=live

# OpenAI
OPENAI_API_KEY=your_openai_key

# CORS
CORS_ORIGINS=["https://zimmerai.com", "https://admin.zimmerai.com"]
```

## 📈 Scalability Considerations

### **Horizontal Scaling**
- **Load Balancer**: Multiple Nginx instances
- **Application Servers**: Multiple FastAPI instances
- **Database**: Read replicas for read-heavy operations
- **CDN**: CloudFlare for static assets

### **Vertical Scaling**
- **CPU**: 4+ cores for high concurrency
- **RAM**: 16GB+ for database and caching
- **Storage**: SSD for database performance
- **Network**: 1Gbps+ for API responses

---

*Architecture documentation generated on September 12, 2025*  
*Version: 2.0.0*  
*Status: Production Ready* ✅
