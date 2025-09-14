import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
// Removed deprecated authenticatedFetch import
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

export default function KBMonitoringDebug() {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    console.log('🔍 KB Monitoring Debug - useEffect triggered');
    console.log('User:', user);
    
    const debugData = {
      user: user,
      timestamp: new Date().toISOString(),
      authContext: 'loaded'
    };
    
    setDebugInfo(debugData);
    setLoading(false);
  }, [user]);

  const testAPI = async () => {
    try {
      console.log('🔍 Testing API call...');
      const res = await fetch('${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}/api/admin/kb-status', {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      console.log('API Response:', res);
      
      if (res.ok) {
        const data = await res.json();
        setDebugInfo((prev: any) => ({ ...prev, apiSuccess: true, apiData: data }));
        console.log('✅ API Success:', data);
      } else {
        const errorText = await res.text();
        setDebugInfo((prev: any) => ({ ...prev, apiError: `${res.status}: ${errorText}` }));
        console.log('❌ API Error:', res.status, errorText);
      }
    } catch (err) {
      console.error('❌ API Exception:', err);
      setDebugInfo((prev: any) => ({ ...prev, apiError: String(err) }));
    }
  };

  if (loading) {
    return (
      <Layout title="Debug - KB Monitoring">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="mr-4">Loading debug info...</span>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Debug - KB Monitoring">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Debug - KB Monitoring</h1>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Debug Information</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">User Authentication:</h3>
              <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
                {JSON.stringify(debugInfo.user, null, 2)}
              </pre>
            </div>
            
            <div>
              <h3 className="font-medium">Timestamp:</h3>
              <p>{debugInfo.timestamp}</p>
            </div>
            
            {debugInfo.apiError && (
              <div>
                <h3 className="font-medium text-red-600">API Error:</h3>
                <p className="text-red-600">{debugInfo.apiError}</p>
              </div>
            )}
            
            {debugInfo.apiSuccess && (
              <div>
                <h3 className="font-medium text-green-600">API Success:</h3>
                <pre className="bg-green-50 p-2 rounded text-sm overflow-auto">
                  {JSON.stringify(debugInfo.apiData, null, 2)}
                </pre>
              </div>
            )}
          </div>
          
          <button
            onClick={testAPI}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Test API Call
          </button>
        </div>
      </div>
    </Layout>
  );
} 