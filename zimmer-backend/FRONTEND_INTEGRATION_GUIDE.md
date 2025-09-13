# Frontend Integration Guide for New Authentication System

## Overview

The new authentication system uses **access/refresh tokens** with **HTTP-only cookies** for enhanced security. This guide shows how to integrate it with your frontend applications.

## Key Features

- ✅ **Access Tokens**: Short-lived (15 minutes) for API requests
- ✅ **Refresh Tokens**: Long-lived (7 days) stored in HTTP-only cookies
- ✅ **Automatic Token Refresh**: Seamless user experience
- ✅ **Session Management**: Database-backed session tracking
- ✅ **Security**: Token rotation, idle timeout, session revocation

## API Endpoints

### Authentication Endpoints

```typescript
// Base URL: ${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/auth

// 1. Login
POST /api/auth/login
Body: { email: string, password: string }
Response: { access_token: string, user: object }
Cookie: refresh_token (HTTP-only)

// 2. Refresh Token
POST /api/auth/refresh
Headers: Cookie: refresh_token
Response: { access_token: string }
Cookie: refresh_token (rotated, HTTP-only)

// 3. Logout
POST /api/auth/logout
Headers: Cookie: refresh_token
Response: { ok: boolean, message: string }
Cookie: refresh_token (cleared)

// 4. Logout All Sessions
POST /api/auth/logout-all
Headers: Authorization: Bearer {access_token}
Response: { ok: boolean, message: string }
```

### User Endpoints

```typescript
// Base URL: ${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/users

// Get current user info
GET /api/users/me
Headers: Authorization: Bearer {access_token}
Response: User object

// Get user profile
GET /api/users/user/profile
Headers: Authorization: Bearer {access_token}
Response: User object
```

## Frontend Integration

### 1. Authentication Context (React)

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE = '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api';

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important: Include cookies
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      setAccessToken(data.access_token);
      setUser(data.user);
      
      // Store user info in localStorage (optional)
      localStorage.setItem('user', JSON.stringify(data.user));
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include', // Important: Include cookies
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      setAccessToken(data.access_token);
    } catch (error) {
      console.error('Token refresh error:', error);
      // Clear auth state on refresh failure
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem('user');
      throw error;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setAccessToken(null);
      localStorage.removeItem('user');
    }
  };

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if we have a stored user
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          
          // Try to refresh token
          await refreshToken();
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear invalid state
        setUser(null);
        setAccessToken(null);
        localStorage.removeItem('user');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      accessToken,
      login,
      logout,
      refreshToken,
      isLoading,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 2. API Client with Automatic Token Refresh

```typescript
// lib/api.ts
class ApiClient {
  private baseURL: string;
  private authContext: any;

  constructor(baseURL: string, authContext: any) {
    this.baseURL = baseURL;
    this.authContext = authContext;
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    // Add auth header if we have a token
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authContext.accessToken) {
      headers.Authorization = `Bearer ${this.authContext.accessToken}`;
    }

    // Always include credentials for cookies
    const config: RequestInit = {
      ...options,
      headers,
      credentials: 'include',
    };

    try {
      const response = await fetch(url, config);
      
      // Handle 401 errors (token expired)
      if (response.status === 401) {
        try {
          // Try to refresh the token
          await this.authContext.refreshToken();
          
          // Retry the original request with new token
          if (this.authContext.accessToken) {
            headers.Authorization = `Bearer ${this.authContext.accessToken}`;
            const retryResponse = await fetch(url, { ...config, headers });
            return retryResponse;
          }
        } catch (refreshError) {
          // Refresh failed, redirect to login
          await this.authContext.logout();
          window.location.href = '/login';
          throw new Error('Authentication required');
        }
      }
      
      return response;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // User endpoints
  async getCurrentUser() {
    const response = await this.makeRequest('/users/me');
    if (!response.ok) throw new Error('Failed to get user info');
    return response.json();
  }

  async getUserProfile() {
    const response = await this.makeRequest('/users/user/profile');
    if (!response.ok) throw new Error('Failed to get user profile');
    return response.json();
  }

  async updateUserProfile(data: any) {
    const response = await this.makeRequest('/users/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update profile');
    return response.json();
  }

  // Dashboard endpoints
  async getUserDashboard() {
    const response = await this.makeRequest('/users/user/dashboard');
    if (!response.ok) throw new Error('Failed to get dashboard');
    return response.json();
  }

  async getUserAutomations() {
    const response = await this.makeRequest('/users/user/automations');
    if (!response.ok) throw new Error('Failed to get automations');
    return response.json();
  }

  // Add more API methods as needed...
}

export default ApiClient;
```

### 3. Login Component

```typescript
// components/LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/router';

export default function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard'); // Redirect to dashboard
    } catch (error: any) {
      setError(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

### 4. Protected Route Component

```typescript
// components/ProtectedRoute.tsx
import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login');
      } else if (requireAdmin && !user.is_admin) {
        router.push('/dashboard');
      }
    }
  }, [user, isLoading, requireAdmin, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user || (requireAdmin && !user.is_admin)) {
    return null;
  }

  return <>{children}</>;
}
```

### 5. App Layout with Auth Provider

```typescript
// pages/_app.tsx (Next.js)
import { AuthProvider } from '../contexts/AuthContext';
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  );
}

export default MyApp;
```

### 6. Dashboard Component Example

```typescript
// pages/dashboard.tsx
import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';
import ApiClient from '../lib/api';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const api = new ApiClient('${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api', { accessToken: user?.accessToken });
        const data = await api.getUserDashboard();
        setDashboardData(data);
      } catch (error) {
        console.error('Failed to fetch dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboard();
    }
  }, [user]);

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span>Welcome, {user?.name}</span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Dashboard content */}
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-4">
            <h2 className="text-2xl font-bold mb-4">Your Dashboard</h2>
            {dashboardData && (
              <div>
                <p>Total Demo Tokens: {dashboardData.total_demo_tokens}</p>
                <p>Total Paid Tokens: {dashboardData.total_paid_tokens}</p>
                {/* Add more dashboard content */}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
```

## Environment Configuration

### Frontend Environment Variables

```env
# .env.local (Next.js)
NEXT_PUBLIC_API_BASE_URL=${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api
NEXT_PUBLIC_BACKEND_URL=${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}
```

### CORS Configuration (Backend)

Make sure your backend has proper CORS configuration:

```python
# In your FastAPI app
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Your frontend URLs
    allow_credentials=True,  # Important for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Best Practices

1. **Always use `credentials: 'include'`** in fetch requests to send cookies
2. **Handle 401 errors** by attempting token refresh
3. **Clear auth state** on logout and refresh failures
4. **Use HTTP-only cookies** (handled automatically by the backend)
5. **Implement proper error handling** for all API calls
6. **Use HTTPS in production** and set `secure: true` for cookies

## Testing the Integration

1. Start the backend server: `uvicorn main:app --host 0.0.0.0 --port 8000`
2. Start your frontend application
3. Navigate to the login page
4. Login with valid credentials
5. Verify that you're redirected to the dashboard
6. Check that API calls work with automatic token refresh
7. Test logout functionality

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured correctly
2. **Cookie Not Set**: Check that `credentials: 'include'` is used
3. **Token Refresh Fails**: Verify the refresh endpoint is working
4. **401 Errors**: Check that access tokens are being sent correctly

### Debug Tips

1. Check browser Network tab for API calls
2. Verify cookies are being set in Application tab
3. Check browser console for errors
4. Use the debug script: `python debug_refresh_issue.py`

## Migration from Old System

If you're migrating from the old JWT-only system:

1. Update your login logic to use the new `/api/auth/login` endpoint
2. Remove manual token storage (localStorage/sessionStorage)
3. Update API calls to use the new ApiClient
4. Test thoroughly to ensure all functionality works

The new system provides better security and user experience while maintaining backward compatibility where possible.
