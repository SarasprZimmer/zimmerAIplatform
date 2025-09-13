import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import TicketForm from '../components/TicketForm';
import { adminAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { TableSkeleton } from '../components/LoadingSkeletons';
import ResponsiveTable from '../components/ResponsiveTable';

interface Ticket {
  id: number;
  user_id: number;
  subject: string;
  message: string;
  status: 'open' | 'pending' | 'resolved';
  importance: string;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  user_name: string;
  assigned_admin_name: string | null;
  attachment_path?: string;
}

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  isAdmin: boolean;
}

interface User {
  id: number;
  name: string;
  is_admin: boolean;
}

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterUser, setFilterUser] = useState('');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [updating, setUpdating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchUsers();
      fetchTickets();
    } else {
      // No user found, skipping data fetch
    }
  }, [user]);

  const fetchUsers = async () => {
    try {
      const usersData = await adminAPI.getUsers();
      setUsers(Array.isArray(usersData) ? usersData : []);
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    }
  };

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filterStatus) params.status = filterStatus;
      if (filterUser) params.user_id = filterUser;
      
      const ticketsData = await adminAPI.getTickets(params);
      setTickets(ticketsData.tickets || []);
    } catch (err) {
      console.error('Error fetching tickets:', err);
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterStatus(e.target.value);
  };

  const handleUserFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterUser(e.target.value);
  };

  const handleStatusUpdate = async (ticketId: number, newStatus: string) => {
    setUpdating(true);
    try {
      await adminAPI.updateTicket(ticketId, { status: newStatus });
      fetchTickets(); // Refresh the list
    } catch (err) {
      console.error('Error updating ticket status:', err);
      // Error is handled by API client
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignTicket = async (ticketId: number, adminId: number) => {
    setUpdating(true);
    try {
      await adminAPI.updateTicket(ticketId, { assigned_to: adminId });
      fetchTickets(); // Refresh the list
    } catch (err) {
      console.error('Error assigning ticket:', err);
      // Error is handled by API client
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
      setSelectedTicket(null);
      fetchTickets(); // Refresh the list
    } catch (err) {
      console.error('Error adding reply:', err);
      // Error is handled by API client
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteTicket = async (ticketId: number) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این تیکت را حذف کنید؟')) return;
    
    setUpdating(true);
    try {
      await adminAPI.deleteTicket(ticketId);
      fetchTickets(); // Refresh the list
    } catch (err) {
      console.error('Error deleting ticket:', err);
      // Error is handled by API client
    } finally {
      setUpdating(false);
    }
  };

  const handleTicketCreated = () => {
    setShowCreateForm(false);
    fetchTickets(); // Refresh the list
  };

  // Parse ticket message to separate original content from replies
  const parseTicketMessages = (ticket: Ticket): { originalMessage: string; messages: Message[] } => {
    const fullMessage = ticket.message;
    const replySeparator = '--- Reply from ';
    
    if (!fullMessage.includes(replySeparator)) {
      // No replies, just original message
      return {
        originalMessage: fullMessage,
        messages: []
      };
    }
    
    const parts = fullMessage.split(replySeparator);
    const originalMessage = parts[0].trim();
    const messages: Message[] = [];
    
    for (let i = 1; i < parts.length; i++) {
      const part = parts[i];
      const endIndex = part.indexOf(' ---');
      
      if (endIndex !== -1) {
        const sender = part.substring(0, endIndex);
        const content = part.substring(endIndex + 4).trim();
        
        messages.push({
          id: `reply-${i}`,
          sender,
          content,
          timestamp: new Date().toISOString(), // We don't have individual timestamps
          isAdmin: sender.toLowerCase().includes('admin') || sender.toLowerCase().includes('مدیر')
        });
      }
    }
    
    return { originalMessage, messages };
  };

  const getImportanceColor = (importance: string | undefined | null) => {
    if (!importance) return 'bg-gray-100 text-gray-800';
    switch (importance.toLowerCase()) {
      case 'low': return 'bg-gray-100 text-gray-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'immediate': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getImportanceText = (importance: string | undefined | null) => {
    if (!importance) return 'نامشخص';
    switch (importance.toLowerCase()) {
      case 'low': return 'کم';
      case 'medium': return 'متوسط';
      case 'immediate': return 'فوری';
      default: return importance;
    }
  };

  useEffect(() => {
    fetchTickets();
    fetchUsers();
  }, [filterStatus, filterUser]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fa-IR') + ' ' + date.toLocaleTimeString('fa-IR');
  };

  const getStatusColor = (status: string | undefined | null) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string | undefined | null) => {
    if (!status) return 'نامشخص';
    switch (status) {
      case 'open': return 'باز';
      case 'pending': return 'در انتظار';
      case 'resolved': return 'حل شده';
      default: return status;
    }
  };

  if (loading) {
    return (
      <Layout title="تیکت‌های پشتیبانی">
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">تیکت‌های پشتیبانی</h2>
              <p className="text-gray-600 mt-2">مدیریت و پاسخ به تیکت‌های پشتیبانی</p>
            </div>
          </div>
          <TableSkeleton rows={5} columns={7} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="تیکت‌های پشتیبانی">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">تیکت‌های پشتیبانی</h2>
            <p className="text-gray-600 mt-2">مدیریت و پاسخ به تیکت‌های پشتیبانی</p>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            {showCreateForm ? 'لغو' : 'ایجاد تیکت'}
          </button>
        </div>

        {/* Create Ticket Form */}
        {showCreateForm && (
          <TicketForm 
            onSuccess={handleTicketCreated}
            userId={user?.id}
          />
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex gap-4 items-center">
              <div className="flex gap-2 items-center">
                <label className="text-sm text-gray-700">وضعیت:</label>
                <select
                  className="border-gray-300 rounded-md"
                  value={filterStatus}
                  onChange={handleStatusFilter}
                >
                  <option value="">همه</option>
                  <option value="open">باز</option>
                  <option value="pending">در انتظار</option>
                  <option value="resolved">حل شده</option>
                </select>
              </div>
              <div className="flex gap-2 items-center">
                <label className="text-sm text-gray-700">کاربر:</label>
                <select
                  className="border-gray-300 rounded-md"
                  value={filterUser}
                  onChange={handleUserFilter}
                >
                  <option value="">همه</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>{user.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={fetchTickets}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? 'در حال بارگذاری...' : 'بروزرسانی'}
            </button>
          </div>
        </div>

        {/* Tickets Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <ResponsiveTable
            columns={[
              {
                key: 'id',
                label: 'شماره',
                mobilePriority: true,
                render: (value: number) => `#${value}`,
                className: 'whitespace-nowrap text-sm text-gray-900'
              },
              {
                key: 'user_name',
                label: 'کاربر',
                mobilePriority: true,
                className: 'whitespace-nowrap text-sm text-gray-900'
              },
              {
                key: 'subject',
                label: 'موضوع',
                mobilePriority: true,
                truncate: true,
                className: 'text-sm text-gray-900 max-w-xs'
              },
              {
                key: 'status',
                label: 'وضعیت',
                mobilePriority: true,
                render: (value: string) => (
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(value)}`}>
                    {getStatusText(value)}
                  </span>
                ),
                className: 'whitespace-nowrap'
              },
              {
                key: 'assigned_admin_name',
                label: 'تخصیص یافته به',
                mobilePriority: false,
                render: (value: string) => value || 'تخصیص نیافته',
                className: 'whitespace-nowrap text-sm text-gray-900'
              },
              {
                key: 'created_at',
                label: 'تاریخ ایجاد',
                mobilePriority: false,
                render: (value: string) => formatDate(value),
                className: 'whitespace-nowrap text-sm text-gray-500'
              },
              {
                key: 'actions',
                label: 'عملیات',
                mobilePriority: true,
                render: (value: any, row: Ticket) => (
                  <div className="space-x-2 space-x-reverse">
                    <button
                      onClick={() => setSelectedTicket(row)}
                      className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                    >
                      مشاهده
                    </button>
                    <select
                      className="text-xs border-gray-300 rounded"
                      value={row.status}
                      onChange={(e) => handleStatusUpdate(row.id, e.target.value)}
                      disabled={updating}
                    >
                      <option value="open">باز</option>
                      <option value="pending">در انتظار</option>
                      <option value="resolved">حل شده</option>
                    </select>
                    <select
                      className="text-xs border-gray-300 rounded"
                      value={row.assigned_to || ''}
                      onChange={(e) => handleAssignTicket(row.id, parseInt(e.target.value))}
                      disabled={updating}
                    >
                      <option value="">تخصیص نیافته</option>
                      {users.filter(u => u.is_admin).map(admin => (
                        <option key={admin.id} value={admin.id}>{admin.name}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => handleDeleteTicket(row.id)}
                      className="text-red-600 hover:text-red-900 text-sm font-medium"
                      disabled={updating}
                    >
                      حذف
                    </button>
                  </div>
                ),
                className: 'whitespace-nowrap text-sm font-medium'
              }
            ]}
            data={tickets}
            emptyMessage="تیکتی یافت نشد."
          />
        </div>

        {/* Ticket Detail Modal */}
        {selectedTicket && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-3/4 shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
              <div className="mt-3">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => setSelectedTicket(null)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      ← بازگشت به تیکت ها
                    </button>
                    <h3 className="text-lg font-medium text-gray-900">تیکت #{selectedTicket.id}</h3>
                  </div>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
                
                {/* Ticket Details */}
                <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedTicket.status)}`}>
                        {getStatusText(selectedTicket.status)}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImportanceColor(selectedTicket.importance)}`}>
                        {getImportanceText(selectedTicket.importance)}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">{formatDate(selectedTicket.created_at)}</span>
                  </div>
                  
                  <h2 className="text-xl font-bold text-gray-900 mb-4">{selectedTicket.subject}</h2>
                  
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-gray-700">{selectedTicket.user_name}</span>
                      <span className="text-xs text-gray-500">کاربر</span>
                    </div>
                    <p className="text-gray-900 whitespace-pre-wrap">
                      {(() => {
                        const parsed = parseTicketMessages(selectedTicket);
                        console.log('Debug - Full message:', selectedTicket.message);
                        console.log('Debug - Parsed original:', parsed.originalMessage);
                        console.log('Debug - Parsed messages:', parsed.messages);
                        return parsed.originalMessage;
                      })()}
                    </p>
                  </div>
                  
                  {selectedTicket.attachment_path && (
                    <div className="mb-4">
                      <a 
                        href={`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/tickets/${selectedTicket.id}/attachment`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                        دانلود فایل پیوست اصلی
                      </a>
                    </div>
                  )}
                </div>

                {/* Chat Section */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">گفتگو</h3>
                  
                  {/* Messages */}
                  <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                    {(() => {
                      const parsed = parseTicketMessages(selectedTicket);
                      console.log('Debug - Chat messages:', parsed.messages);
                      return parsed.messages.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">هنوز پیامی ارسال نشده است.</div>
                      ) : (
                        parsed.messages.map((message) => (
                          <div key={message.id} className={`flex ${message.isAdmin ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.isAdmin 
                                ? 'bg-blue-500 text-white' 
                                : 'bg-gray-200 text-gray-900'
                            }`}>
                              <div className="text-xs opacity-75 mb-1">{message.sender}</div>
                              <div className="whitespace-pre-wrap">{message.content}</div>
                            </div>
                          </div>
                        ))
                      );
                    })()}
                  </div>
                  
                  {/* Reply Input */}
                  <div className="border-t pt-4">
                    <textarea
                      className="w-full border-gray-300 rounded-lg shadow-sm resize-none"
                      rows={3}
                      value={replyMessage}
                      onChange={(e) => setReplyMessage(e.target.value)}
                      placeholder="پیام خود را بنویسید...."
                    />
                    <div className="flex justify-between items-center mt-3">
                      <div className="flex items-center gap-2">
                        <input
                          type="file"
                          className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                      </div>
                      <button
                        onClick={() => handleReply(selectedTicket.id)}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        disabled={updating || !replyMessage.trim()}
                      >
                        {updating ? 'در حال ارسال...' : 'ارسال'}
                      </button>
                    </div>
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