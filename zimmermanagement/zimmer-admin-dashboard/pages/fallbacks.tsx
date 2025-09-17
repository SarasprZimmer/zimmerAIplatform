import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface Client {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface Fallback {
  id: number;
  client_id: number;
  client_name: string;
  message: string;
  created_at: string;
  status: string;
}

export default function Fallbacks() {
  const [fallbacks, setFallbacks] = useState<Fallback[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterClient, setFilterClient] = useState<string>('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchClients();
      fetchFallbacks();
    }
    // eslint-disable-next-line
  }, [user]);

  const fetchClients = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setClients(data.users || []);
      } else {
        console.log('Users endpoint not implemented, using empty list');
        setClients([]);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
      setClients([]);
    }
  };

  const fetchFallbacks = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filterClient) params.client_id = filterClient;
      
      // Build query string
      const query = new URLSearchParams(params).toString();
      const url = '/api/admin/fallbacks' + (query ? `?${query}` : '');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://193.162.129.243:8000'}${url}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setFallbacks(data.fallbacks || []);
      } else {
        console.log('Fallbacks endpoint not implemented, using empty list');
        setFallbacks([]);
      }
    } catch (error) {
      console.error('Error fetching fallbacks:', error);
      setFallbacks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterClient(e.target.value);
  };

  const applyFilters = () => {
    fetchFallbacks();
  };

  useEffect(() => {
    if (filterClient !== '') {
      fetchFallbacks();
    }
  }, [filterClient]);

  return (
    <Layout title="Fallbacks">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Fallbacks</h1>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Client
              </label>
              <select
                value={filterClient}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Clients</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.name} ({client.email})
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={applyFilters}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>

        {/* Fallbacks Table */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            {loading ? (
              <div className="text-center py-4">
                <div className="text-lg">Loading fallbacks...</div>
              </div>
            ) : fallbacks.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 text-lg">No fallbacks found</div>
                <div className="text-gray-400 text-sm mt-2">
                  Fallbacks will appear here when users encounter issues
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Client
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Message
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created At
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {fallbacks.map((fallback) => (
                      <tr key={fallback.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {fallback.client_name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {fallback.message}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            fallback.status === 'resolved' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {fallback.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(fallback.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
