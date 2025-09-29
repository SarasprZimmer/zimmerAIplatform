import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { adminAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

interface Ticket {
  id: number;
  user_id: number;
  subject: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
  user_name?: string;
  assigned_to?: number;
  assigned_admin?: string;
  messages?: TicketMessage[];
}

interface TicketMessage {
  id: number;
  ticket_id: number;
  message: string;
  is_admin: boolean;
  created_at: string;
  admin_name?: string;
}

// Function to parse concatenated messages
const parseTicketMessages = (messageString: string) => {
  if (!messageString) return [];
  
  const messages = [];
  const parts = messageString.split('---');
  
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i].trim();
    if (part) {
      // Check if it's a reply from admin
      if (part.includes('Reply from UniAI Manager') || part.includes('Reply from')) {
        messages.push({
          id: i,
          message: part.replace(/^Reply from [^-]+ --- /, ''),
          is_admin: true,
          created_at: new Date().toISOString()
        });
      } else {
        messages.push({
          id: i,
          message: part,
          is_admin: false,
          created_at: new Date().toISOString()
        });
      }
    }
  }
  
  return messages;
};

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [updating, setUpdating] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTickets();
    }
  }, [user]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const data = await adminAPI.getTickets();
      setTickets(data.tickets || []);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    setUpdating(true);
    try {
      await adminAPI.updateTicket(ticketId, { status: newStatus });
      fetchTickets();
    } catch (err) {
      console.error('Error updating ticket status:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleReply = async (ticketId: number) => {
    if (!replyMessage.trim()) return;
    
    setUpdating(true);
    try {
      await adminAPI.updateTicket(ticketId, { message: replyMessage });
      setReplyMessage('');
      fetchTickets();
    } catch (err) {
      console.error('Error replying to ticket:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteTicket = async (ticketId: number) => {
    if (!confirm('Are you sure you want to delete this ticket?')) return;
    
    setUpdating(true);
    try {
      await adminAPI.deleteTicket(ticketId);
      fetchTickets();
    } catch (err) {
      console.error('Error deleting ticket:', err);
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'closed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout title="تیکت‌های پشتیبانی">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">در حال بارگذاری تیکت‌ها...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="تیکت‌های پشتیبانی">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">تیکت‌های پشتیبانی</h1>
          <button
            onClick={fetchTickets}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            به‌روزرسانی
          </button>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            {tickets.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 text-lg">هیچ تیکتی یافت نشد</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        شناسه
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        کاربر
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        موضوع
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        وضعیت
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        اولویت
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        تاریخ ایجاد
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        عملیات
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tickets.map((ticket) => (
                      <tr key={ticket.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          #{ticket.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {ticket.user_name || `User ${ticket.user_id}`}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                          {ticket.subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <select
                            value={ticket.status}
                            onChange={(e) => handleStatusChange(ticket.id, e.target.value)}
                            disabled={updating}
                            className={`text-xs font-semibold rounded-full px-2 py-1 ${getStatusColor(ticket.status)}`}
                          >
                            <option value="open">Open</option>
                            <option value="in_progress">In Progress</option>
                            <option value="resolved">Resolved</option>
                            <option value="closed">Closed</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(ticket.priority)}`}>
                            {ticket.priority}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(ticket.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => setSelectedTicket(ticket)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            View
                          </button>
                          <button
                            onClick={() => handleDeleteTicket(ticket.id)}
                            disabled={updating}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Ticket Detail Modal */}
        {selectedTicket && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Ticket #{selectedTicket.id} - {selectedTicket.subject}
                  </h3>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>User:</strong> {selectedTicket.user_name || `User ${selectedTicket.user_id}`}
                  </p>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Status:</strong> 
                    <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedTicket.status)}`}>
                      {selectedTicket.status}
                    </span>
                  </p>
                  <p className="text-sm text-gray-600 mb-4">
                    <strong>Priority:</strong> 
                    <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(selectedTicket.priority)}`}>
                      {selectedTicket.priority}
                    </span>
                  </p>
                  
                  {/* Messages Display */}
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {parseTicketMessages(selectedTicket.description).map((message, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg ${
                          message.is_admin
                            ? 'bg-blue-50 border-l-4 border-blue-400 ml-8'
                            : 'bg-gray-50 border-l-4 border-gray-400 mr-8'
                        }`}
                      >
                        <div className="flex justify-between items-start mb-1">
                          <span className={`text-xs font-medium ${
                            message.is_admin ? 'text-blue-600' : 'text-gray-600'
                          }`}>
                            {message.is_admin ? 'Admin' : selectedTicket.user_name || 'User'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(message.created_at).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-800">{message.message}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Reply Section */}
                <div className="border-t pt-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Reply to Ticket</h4>
                  <textarea
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    placeholder="Type your reply here..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="mt-2 flex justify-end">
                    <button
                      onClick={() => handleReply(selectedTicket.id)}
                      disabled={updating || !replyMessage.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {updating ? 'Sending...' : 'Send Reply'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
