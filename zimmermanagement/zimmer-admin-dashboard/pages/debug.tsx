import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';
import api from '../lib/api';

export default function Debug() {
  const { user, isAuthenticated, logout } = useAuth();
  const [token, setToken] = useState<string | null>(null);
  const [apiTest, setApiTest] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setToken(authClient.getAccessToken());
  }, []);

  const testApi = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/admin/users');
      setApiTest(`Status: ${response.status}\nData: ${JSON.stringify(response.data, null, 2)}`);
    } catch (error: any) {
      setApiTest(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setToken(null);
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Debug Page</h1>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          <div className="space-y-2">
            <p><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
            <p><strong>Token:</strong> {token ? `${token.substring(0, 20)}...` : 'None'}</p>
            <p><strong>User:</strong> {user ? JSON.stringify(user) : 'None'}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="space-x-4">
            <button
              onClick={testApi}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Testing...' : 'Test API'}
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
            <button
              onClick={clearAuth}
              className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
            >
              Clear Auth Data
            </button>
          </div>
        </div>

        {apiTest && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">API Test Result</h2>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {apiTest}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
} 