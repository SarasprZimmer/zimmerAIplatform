import React, { useState, useEffect } from 'react';
import { adminAPI } from '../lib/api';

interface Client {
  id: number;
  name: string;
}

interface KnowledgeFormProps {
  onAdd: () => void;
}

const KnowledgeForm: React.FC<KnowledgeFormProps> = ({ onAdd }) => {
  const [clients, setClients] = useState<Client[]>([]);
  const [clientId, setClientId] = useState<number | ''>('');
  const [category, setCategory] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const data = await adminAPI.getUsers();
      setClients(Array.isArray(data.users) ? data.users : []);
    } catch (error) {
      console.log('Failed to fetch users, using empty list:', error);
      setClients([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess('');
    setError('');
    try {
      await adminAPI.createKnowledge({
        client_id: clientId,
        category,
        answer,
      });
      
      setSuccess('Knowledge entry added!');
      setClientId('');
      setCategory('');
      setAnswer('');
      onAdd();
    } catch (err) {
      setError('Failed to add knowledge entry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Add Knowledge Entry</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Client</label>
          <select
            className="w-full border-gray-300 rounded-md"
            value={clientId}
            onChange={e => setClientId(Number(e.target.value))}
            required
          >
            <option value="">Select client</option>
            {clients.map(client => (
              <option key={client.id} value={client.id}>{client.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <input
            type="text"
            className="w-full border-gray-300 rounded-md"
            value={category}
            onChange={e => setCategory(e.target.value)}
            placeholder="e.g. visa, pricing"
            required
          />
        </div>
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Answer</label>
          <textarea
            className="w-full border-gray-300 rounded-md min-h-[40px]"
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            placeholder="Enter answer..."
            required
          />
        </div>
      </div>
      <div className="flex items-center gap-4 mt-2">
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Adding...' : 'Add Entry'}
        </button>
        {success && <span className="text-green-600 text-sm">{success}</span>}
        {error && <span className="text-red-600 text-sm">{error}</span>}
      </div>
    </form>
  );
};

export default KnowledgeForm; 