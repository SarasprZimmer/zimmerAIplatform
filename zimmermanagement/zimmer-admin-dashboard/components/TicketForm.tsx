import React, { useState } from 'react';
// Removed deprecated authenticatedFetch import
import { authClient } from '../lib/auth-client';

interface TicketFormProps {
  onSuccess?: () => void;
  userId?: number;
}

const TicketForm: React.FC<TicketFormProps> = ({ onSuccess, userId }) => {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccess('');
    setError('');
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/tickets`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId || 1, // Default to user ID 1 if not provided
          subject,
          message,
        }),
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }
      
      setSuccess('تیکت با موفقیت ایجاد شد!');
      setSubject('');
      setMessage('');
      onSuccess?.();
    } catch (err) {
      console.error('Error creating ticket:', err);
      setError('خطا در ایجاد تیکت. لطفاً دوباره تلاش کنید.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">ایجاد تیکت پشتیبانی</h3>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">موضوع</label>
        <input
          type="text"
          className="w-full border-gray-300 rounded-md"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="توضیح مختصر مشکل شما"
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">پیام</label>
        <textarea
          className="w-full border-gray-300 rounded-md min-h-[120px]"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="لطفاً مشکل خود را به تفصیل توضیح دهید..."
          required
        />
      </div>
      
      <div className="flex items-center gap-4 mt-2">
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'در حال ایجاد...' : 'ایجاد تیکت'}
        </button>
        {success && <span className="text-green-600 text-sm">{success}</span>}
        {error && <span className="text-red-600 text-sm">{error}</span>}
      </div>
    </form>
  );
};

export default TicketForm; 