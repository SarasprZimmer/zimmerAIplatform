import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import KnowledgeForm from '../components/KnowledgeForm';
import KnowledgeTable from '../components/KnowledgeTable';
import { adminAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { TableSkeleton } from '../components/LoadingSkeletons';

interface Client {
  id: number;
  name: string;
}

interface KnowledgeEntry {
  id: number;
  client_id: number;
  client_name: string;
  category: string;
  answer: string;
  created_at: string;
}

export default function Knowledge() {
  const [clients, setClients] = useState<Client[]>([]);
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterClient, setFilterClient] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchClients();
      fetchEntries();
    } else {
      // No user found, skipping data fetch
    }
    // eslint-disable-next-line
  }, [user]);

  const fetchClients = async () => {
    try {
      const usersData = await adminAPI.getUsers();
      setClients(Array.isArray(usersData) ? usersData : []);
    } catch (err) {
      console.error('Error fetching clients:', err);
      setClients([]); // Defensive: set to empty array on error
    }
  };

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filterClient) params.client_id = filterClient;
      if (filterCategory) params.category = filterCategory;
      
      const data = await adminAPI.getKnowledgeBases(params);
      
      // Map client_id to client_name
      const clientMap: Record<number, string> = {};
      clients.forEach(c => { clientMap[c.id] = c.name; });
      
      const mapped = data.knowledge_entries.map((k: any) => ({
        ...k,
        client_name: k.client_name || clientMap[k.client_id] || `Client ${k.client_id}`,
      }));
      setEntries(mapped);
    } catch (err) {
      console.error('Error fetching knowledge entries:', err);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  // Refresh entries after add
  const handleAdd = () => {
    fetchEntries();
  };

  // Filter handlers
  const handleClientFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterClient(e.target.value);
  };
  const handleCategoryFilter = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilterCategory(e.target.value);
  };
  useEffect(() => {
    fetchEntries();
    // eslint-disable-next-line
  }, [filterClient, filterCategory]);

  return (
    <Layout title="Knowledge Base">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Knowledge Base</h2>
          <p className="text-gray-600 mt-2">Manage client-specific knowledge entries</p>
        </div>
        <KnowledgeForm onAdd={handleAdd} />
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
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-700">Search Category:</label>
              <input
                type="text"
                className="border-gray-300 rounded-md"
                value={filterCategory}
                onChange={handleCategoryFilter}
                placeholder="e.g. visa, pricing"
              />
            </div>
          </div>
          {loading ? (
            <TableSkeleton rows={5} columns={4} />
          ) : (
            <KnowledgeTable entries={entries} />
          )}
        </div>
      </div>
    </Layout>
  );
} 