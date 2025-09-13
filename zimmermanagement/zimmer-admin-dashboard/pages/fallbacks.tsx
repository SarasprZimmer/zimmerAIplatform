import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import FallbackTable from '../components/FallbackTable';
// Removed deprecated authenticatedFetch import
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface Client {
  id: number;
  name: string;
}

interface FallbackEntry {
  id: number;
  client_id: number;
  client_name: string;
  question: string;
  created_at: string;
}

export default function Fallbacks() {
  const [clients, setClients] = useState<Client[]>([]);
  const [entries, setEntries] = useState<FallbackEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterClient, setFilterClient] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchClients();
      fetchEntries();
    }
    // eslint-disable-next-line
  }, [user]);

  const fetchClients = async () => {
    try {
      const res = await fetch('${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.status === 404) {
        console.log('Users endpoint not implemented, using empty list');
        setClients([]);
        return;
      }
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      setClients(Array.isArray(data.users) ? data.users : []);
    } catch {
      setClients([]); // Defensive: set to empty array on error
    }
  };

  const fetchEntries = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = {};
      if (filterClient) params.client_id = filterClient;
      // Build query string
      const query = new URLSearchParams(params).toString();
      const url = '/api/admin/fallbacks' + (query ? `?${query}` : '');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}${url}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await res.json();
      // Map client_id to client_name
      const clientMap: Record<number, string> = {};
      clients.forEach(c => { clientMap[c.id] = c.name; });
      const fallbackArr = Array.isArray(data.fallbacks) ? data.fallbacks : (Array.isArray(data.fallback_entries) ? data.fallback_entries : []);
      const mapped = fallbackArr.map((f: any) => ({
        ...f,
        client_name: f.client_name || clientMap[f.client_id] || f.client_id,
      }));
      // Sort by newest first
      setEntries(mapped.sort((a: FallbackEntry, b: FallbackEntry) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
    } catch {
      setEntries([]); // Defensive: set to empty array on error
    } finally {
      setLoading(false);
    }
  };

  // Filter handler
  const handleClientFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterClient(e.target.value);
  };
  useEffect(() => {
    fetchEntries();
    // eslint-disable-next-line
  }, [filterClient]);

  return (
    <Layout title="Fallback Logs">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Fallback Logs</h2>
          <p className="text-gray-600 mt-2">Review unanswered questions and improve your knowledge base</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-700">Filter by Client:</label>
              <select
                className="border-gray-300 rounded-md"
                value={filterClient}
                onChange={handleClientFilter}
              >
                <option value="">All</option>
                {clients.map(client => (
                  <option key={client.id} value={client.id}>{client.name}</option>
                ))}
              </select>
            </div>
            <div className="text-sm text-gray-500 font-semibold">
              Total Fallbacks: <span className="text-blue-600">{entries.length}</span>
            </div>
          </div>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Loading fallback entries...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12 text-red-600">{error}</div>
          ) : (
            <FallbackTable entries={entries} />
          )}
        </div>
      </div>
    </Layout>
  );
} 