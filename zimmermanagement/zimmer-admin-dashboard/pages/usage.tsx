import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import UsageTable from '../components/UsageTable';
// Removed deprecated authenticatedFetch import
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface UsageRecord {
  id: number;
  date: string;
  usage_type: string;
  description?: string;
  tokens_used: number;
}

export default function Usage() {
  const [usage, setUsage] = useState<UsageRecord[]>([]);
  const [totalUsage, setTotalUsage] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) fetchUsage();
    // eslint-disable-next-line
  }, [user]);

  const fetchUsage = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!user) return;
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/usage/stats`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Usage stats response:', data);
      
      // For now, show the stats data instead of individual records
      // Since we don't have individual user usage records yet
      setUsage([]); // No individual records available yet
      setTotalUsage(data.total_tokens_used || 0);
    } catch (err) {
      setError('Failed to load usage data.');
      setUsage([]); // Defensive: set to empty array on error
      setTotalUsage(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Token Usage">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">System Usage Statistics</h2>
          <p className="text-gray-600 mt-2">Monitor overall AI token consumption and system usage patterns</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Usage Statistics</h3>
            <span className="text-sm text-gray-500">Total Tokens Used: <span className="font-semibold text-blue-600">{totalUsage}</span></span>
            <button
              onClick={fetchUsage}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Refresh
            </button>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Loading usage data...</span>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-600 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Usage Data</h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                  onClick={fetchUsage}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Try Again
                </button>
              </div>
            ) : (
              <UsageTable records={usage} />
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
} 