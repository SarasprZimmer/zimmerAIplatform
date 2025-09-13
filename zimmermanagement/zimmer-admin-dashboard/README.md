# Zimmer Admin Dashboard

A comprehensive admin panel for managing the Zimmer system, built with Next.js, TypeScript, and Tailwind CSS.

## 🚀 Current Status

**✅ BUILD STATUS: SUCCESSFUL**
- All TypeScript compilation errors resolved
- All missing API methods implemented
- Component type mismatches fixed
- Ready for development and production

## 🛠️ Recent Fixes Applied

### Type Errors Resolved
- **Sidebar.tsx**: Fixed `user?.role !== 'manager'` to `!user?.is_admin`
- **clients.tsx**: Fixed `CardSkeleton count={6}` prop usage
- **knowledge.tsx**: Fixed `adminAPI.getKnowledge()` to `adminAPI.getKnowledgeBases()`
- **tickets.tsx**: Fixed missing `<ResponsiveTable` opening tag
- **signup.tsx**: Added missing `signup` method to AuthContext and authAPI
- **users.tsx**: Added missing `createUser` method to adminAPI

### API Methods Added
- `authAPI.signup()` - User registration functionality
- `adminAPI.getUserAutomations()` - Fetch user automations
- `adminAPI.deleteTicket()` - Delete support tickets
- `adminAPI.createUser()` - Create new users

## 🎯 Features

### Core Management
- **Dashboard Overview**: Key metrics and statistics with real-time updates
- **User Management**: Create, update, and delete users with role-based access
- **Client Management**: View and manage registered clients and their automations
- **Support Tickets**: Comprehensive ticket management system with status tracking

### AI & Automation
- **Knowledge Base**: Manage AI responses and knowledge entries by client
- **Token Usage**: Monitor AI token consumption and balance management
- **User Automations**: Track user automation status and demo tokens
- **Fallback Logs**: Monitor unanswered questions and system performance

### System Administration
- **Payments**: Track revenue and payment history
- **Backup Management**: System backup creation and restoration
- **API Keys**: Manage OpenAI and other service integrations
- **System Monitoring**: Real-time system status and health checks

## 🏗️ Tech Stack

### Frontend Framework
- **Next.js 14.2.30** with TypeScript 5
- **React 18** with modern hooks and context API
- **TailwindCSS 3.3.0** for responsive styling

### Development Tools
- **TypeScript 5** for type safety
- **ESLint** for code quality
- **PostCSS** for CSS processing
- **Autoprefixer** for browser compatibility

### HTTP & State Management
- **Axios** with interceptors for API communication
- **React Context** for global state management
- **JWT** authentication with automatic token refresh

## 🚀 Getting Started

### Prerequisites
- **Node.js 20+** (recommended for Next.js 14)
- **npm** or **yarn** package manager

### Installation

1. **Clone and navigate to project:**
```bash
cd zimmermanagement/zimmer-admin-dashboard
npm install
```

2. **Environment Configuration:**
The project includes a `.env` file with default settings. For development, create `.env.local`:
```bash
# Copy existing .env file
cp .env .env.local
```

3. **Environment Variables:**
```env
NEXT_PUBLIC_API_URL=${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}
NODE_ENV=development
PORT=4000
NEXT_PUBLIC_ENABLE_DEBUG=true
```

4. **Start Development Server:**
```bash
npm run dev
```

5. **Access the Application:**
Open [http://localhost:4000](http://localhost:4000) in your browser.

**Note**: The development server runs on port 4000 as configured in the environment.

## 📁 Project Structure

```
zimmer-admin-dashboard/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout wrapper with authentication
│   ├── Sidebar.tsx     # Navigation sidebar with role-based access
│   ├── Topbar.tsx      # Top navigation bar
│   ├── ResponsiveTable.tsx # Data table component
│   ├── LoadingSkeletons.tsx # Loading state components
│   └── Toast.tsx       # Notification system
├── contexts/           # React context providers
│   └── AuthContext.tsx # Authentication and user management
├── lib/                # Utility libraries and API
│   ├── api.ts          # Axios API client with interceptors
│   ├── auth-client.ts  # Client-side authentication utilities
│   └── keep-alive.ts   # Session management
├── pages/              # Next.js page components
│   ├── index.tsx       # Dashboard home with metrics
│   ├── users.tsx       # User management
│   ├── clients.tsx     # Client management
│   ├── knowledge.tsx   # Knowledge base
│   ├── tickets.tsx     # Support ticket system
│   ├── usage.tsx       # Token usage monitoring
│   ├── payments.tsx    # Payment tracking
│   ├── fallbacks.tsx   # Fallback logs
│   └── signup.tsx      # User registration
├── styles/             # Global styles
│   ├── globals.css     # TailwindCSS imports
│   └── mobile.css      # Mobile-specific styles
├── public/             # Static assets and fonts
└── .env                # Environment configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🔌 API Integration

The dashboard connects to the Zimmer backend API at `${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}`. Make sure your backend server is running before using the dashboard.

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login with email/password
- `POST /api/auth/signup` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Token refresh
- `GET /api/me` - Get current user information

#### User Management
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `GET /api/admin/users/{id}` - Get user details
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user

#### Support System
- `GET /api/admin/tickets` - List support tickets
- `POST /api/admin/tickets` - Create new ticket
- `GET /api/admin/tickets/{id}` - Get ticket details
- `PUT /api/admin/tickets/{id}` - Update ticket
- `DELETE /api/admin/tickets/{id}` - Delete ticket

#### Knowledge Base
- `GET /api/admin/knowledge` - List knowledge entries
- `GET /api/admin/knowledge/{id}` - Get knowledge entry
- `PUT /api/admin/knowledge/{id}` - Update knowledge entry

#### System Management
- `GET /api/admin/backups` - List system backups
- `POST /api/admin/backups` - Create new backup
- `GET /api/admin/system/status` - Get system status
- `GET /api/admin/usage` - Get usage statistics

## Customization

- **Colors**: Modify `tailwind.config.js` to add custom colors
- **Layout**: Edit `components/Layout.tsx` for layout changes
- **Navigation**: Update `components/Sidebar.tsx` for menu changes
- **Styling**: Use TailwindCSS classes throughout the application

## 🧪 Testing & Quality Assurance

### Build Status
- **✅ TypeScript Compilation**: All type errors resolved
- **✅ Component Rendering**: All components render without errors
- **✅ API Integration**: All required API methods implemented
- **✅ Authentication Flow**: Complete login/logout/signup functionality

### Testing Commands
```bash
# Build the application
npm run build

# Run linting
npm run lint

# Type checking
npx tsc --noEmit
```

## 🚀 Deployment

### Production Build
1. **Build the application:**
```bash
npm run build
```

2. **Start the production server:**
```bash
npm run start
```

### Direct Server Deployment
```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Platform Deployment
Deploy to Vercel, Netlify, or your preferred hosting platform.

## 🔍 Troubleshooting

### Common Issues & Solutions

#### Build Errors
- **All TypeScript errors have been resolved** ✅
- **Component type mismatches fixed** ✅
- **Missing API methods implemented** ✅

#### Runtime Issues
- **API Connection**: Ensure backend is running on configured URL
- **Authentication**: Check token validity and refresh mechanism
- **Environment Variables**: Verify `.env.local` configuration

#### Performance Issues
- **Bundle Size**: Optimized with Next.js 14 features
- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components load on demand

### Debug Mode
Enable debug mode by setting `NEXT_PUBLIC_ENABLE_DEBUG=true` in environment variables.

## 📈 Performance Metrics

- **Build Time**: Optimized for fast development
- **Bundle Size**: Efficient code splitting
- **Runtime Performance**: Optimized React components
- **Mobile Responsiveness**: Touch-friendly interface

## 🔐 Security Features

- **Protected Routes**: Authentication required for all admin pages
- **Role-Based Access**: Admin-only features properly restricted
- **JWT Tokens**: Secure authentication with automatic refresh
- **HTTP-Only Cookies**: Secure token storage
- **CSRF Protection**: Built-in security measures

## 🌐 Internationalization

- **Persian (Farsi) Support**: Complete RTL language support
- **Localized UI**: Persian text throughout the interface
- **RTL Layout**: Right-to-left text direction support
- **Persian Dates**: Localized date formatting

## 📱 Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Responsive Tables**: Adaptive data display
- **Touch Interface**: Mobile-friendly controls
- **Progressive Enhancement**: Works on all device sizes

---

**Last Updated**: September 1, 2025  
**Build Status**: ✅ Successful  
**Version**: 0.1.0  
**Next.js**: 14.2.30  
**TypeScript**: 5  
**Node.js**: 20+ (recommended) 