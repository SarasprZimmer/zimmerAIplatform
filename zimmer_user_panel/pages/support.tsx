'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import { Card } from '@/components/Skeleton';
import { apiFetch } from '@/lib/apiClient';

type Ticket = {
  id: number;
  subject: string;
  category: 'financial' | 'tech' | 'customer';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  updated_at: string;
  messages: Array<{
    id: string;
    content: string;
    is_from_user: boolean;
    created_at: string;
  }>;
};

type FAQ = {
  id: number;
  question: string;
  answer: string;
  category: string;
};

// FAQ data - static content (moved outside component to avoid re-creation)
const staticFaqs: FAQ[] = [
  {
    id: 1,
    question: 'چطور می‌تونم اتوماسیون جدید خریداری کنم؟',
    answer: 'برای خرید اتوماسیون جدید، به صفحه اتوماسیون‌ها بروید و روی "خرید" کلیک کنید. سپس مراحل پرداخت را تکمیل کنید.',
    category: 'خرید'
  },
  {
    id: 2,
    question: 'چطور می‌تونم وضعیت پرداخت رو چک کنم؟',
    answer: 'برای بررسی وضعیت پرداخت، به بخش "پرداخت‌ها" در داشبورد خود بروید. تمام تراکنش‌های شما در آنجا نمایش داده می‌شود.',
    category: 'پرداخت'
  },
  {
    id: 3,
    question: 'چطور می‌تونم پشتیبانی فنی دریافت کنم؟',
    answer: 'برای دریافت پشتیبانی فنی، از طریق همین صفحه تیکت جدید ایجاد کنید یا با تیم پشتیبانی ما تماس بگیرید.',
    category: 'پشتیبانی'
  },
  {
    id: 4,
    question: 'چطور می‌تونم حساب کاربری خود را حذف کنم؟',
    answer: 'برای حذف حساب کاربری، به بخش تنظیمات بروید و روی "حذف حساب" کلیک کنید. توجه داشته باشید که این عمل غیرقابل بازگشت است.',
    category: 'حساب کاربری'
  }
];


// Parse concatenated ticket messages into individual messages
const parseTicketMessages = (messageString: string, ticketId: number, createdAt: string) => {
  const messages = [];
  
  // Split by the separator pattern "--- Reply from [Name] ---"
  const parts = messageString.split(/\n\n--- Reply from .+ ---\n/);
  
  // First part is the original user message
  if (parts[0].trim()) {
    messages.push({
      id: `${ticketId}-0`,
      content: parts[0].trim(),
      is_from_user: true,
      created_at: createdAt
    });
  }
  
  // Parse subsequent parts (admin replies)
  for (let i = 1; i < parts.length; i++) {
    if (parts[i].trim()) {
      messages.push({
        id: `${ticketId}-${i}`,
        content: parts[i].trim(),
        is_from_user: false, // Admin replies
        created_at: createdAt
      });
    }
  }
  
  return messages;
};


export default function SupportPage() {
  const { isAuthenticated, loading, user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'tickets' | 'faq' | 'new'>('tickets');
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loadingTickets, setLoadingTickets] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [newTicket, setNewTicket] = useState<{
    subject: string;
    category: 'financial' | 'tech' | 'customer';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    description: string;
  }>({
    subject: '',
    category: 'tech',
    priority: 'medium',
    description: ''
  });

  // Handle URL parameters for pre-selection
  useEffect(() => {
    const { category, tab } = router.query;
    
    if (tab === 'new') {
      setActiveTab('new');
    }
    
    if (category && ['financial', 'tech', 'customer'].includes(category as string)) {
      setNewTicket(prev => ({
        ...prev,
        category: category as 'financial' | 'tech' | 'customer'
      }));
    }
  }, [router.query]);


  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  const fetchTickets = useCallback(async () => {
    if (!user) return;
    
    try {
      const response = await apiFetch('/api/tickets', {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        // Convert backend tickets to frontend format
        const formattedTickets: Ticket[] = data.tickets.map((ticket: any) => ({
          id: ticket.id,
          subject: ticket.subject,
          category: 'tech', // Default category since backend doesn't store this
          status: ticket.status,
          priority: ticket.importance,
          created_at: ticket.created_at,
          updated_at: ticket.updated_at,
          messages: parseTicketMessages(ticket.message, ticket.id, ticket.created_at)
        }));
        setTickets(formattedTickets);
      } else {
        console.error('Failed to fetch tickets:', response.status);
        setTickets([]);
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
      setTickets([]);
    }
  }, [user]);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingTickets(true);
    
    try {
      // Check if user is authenticated
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Create form data for the API call
      const formData = new FormData();
      formData.append('user_id', user.id.toString());
      formData.append('subject', newTicket.subject);
      formData.append('message', newTicket.description);
      formData.append('importance', newTicket.priority);

      // Make API call to create ticket
      const response = await apiFetch('/api/tickets', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Failed to create ticket: ${response.status}`);
      }

      const createdTicket = await response.json();
      
      // Convert backend ticket format to frontend format
      const newTicketData: Ticket = {
        id: createdTicket.id,
        subject: createdTicket.subject,
        category: newTicket.category, // Keep the category from form
        status: createdTicket.status,
        priority: createdTicket.importance,
        created_at: createdTicket.created_at,
        updated_at: createdTicket.updated_at,
        messages: parseTicketMessages(createdTicket.message, createdTicket.id, createdTicket.created_at)
      };
      
      setTickets(prev => [newTicketData, ...prev]);
      setNewTicket({ subject: '', category: 'tech', priority: 'medium', description: '' });
      setActiveTab('tickets');
      
    } catch (error) {
      console.error('Error creating ticket:', error);
      alert('خطا در ایجاد تیکت. لطفاً دوباره تلاش کنید.');
    } finally {
      setLoadingTickets(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchTickets();
    }
    // Set static FAQ data
    setFaqs(staticFaqs);
  }, [user, fetchTickets]);

  const handleSendMessage = async (ticketId: number) => {
    if (!newMessage.trim()) return;
    
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket) return;
    
    try {
      // Make API call to update ticket with new message
      const response = await apiFetch(`/api/tickets/${ticketId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: newMessage
        })
      });

      if (response.ok) {
        // Refresh tickets to get updated data
        await fetchTickets();
        setNewMessage('');
      } else {
        console.error('Failed to send message:', response.status);
        alert('خطا در ارسال پیام. لطفاً دوباره تلاش کنید.');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('خطا در ارسال پیام. لطفاً دوباره تلاش کنید.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'text-red-600 bg-red-100';
      case 'in_progress': return 'text-yellow-600 bg-yellow-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'closed': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6" dir="rtl">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">پشتیبانی</h1>
          <p className="text-gray-600">در اینجا می‌توانید تیکت‌های پشتیبانی خود را مدیریت کنید و سوالات متداول را مشاهده کنید.</p>
          {router.query.category && (
            <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-xl">
              <p className="text-sm text-purple-700">
                <span className="font-medium">دسته‌بندی انتخاب شده:</span> {
                  router.query.category === 'financial' ? 'پشتیبانی مالی' :
                  router.query.category === 'tech' ? 'پشتیبانی فنی' :
                  router.query.category === 'customer' ? 'امور مشتریان' : ''
                }
              </p>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <div className="flex space-x-4 mb-6">
            <button
              onClick={() => setActiveTab('tickets')}
              className={`px-6 py-3 rounded-xl font-medium transition-colors ${
                activeTab === 'tickets' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              تیکت‌های من
            </button>
            <button
              onClick={() => setActiveTab('faq')}
              className={`px-6 py-3 rounded-xl font-medium transition-colors ${
                activeTab === 'faq' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              سوالات متداول
            </button>
            <button
              onClick={() => setActiveTab('new')}
              className={`px-6 py-3 rounded-xl font-medium transition-colors ${
                activeTab === 'new' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              تیکت جدید
            </button>
          </div>

          {/* Tickets Tab */}
          {activeTab === 'tickets' && (
            <div className="space-y-4">
              {tickets.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  هیچ تیکتی یافت نشد
                </div>
              ) : (
                tickets.map(ticket => (
                  <Card key={ticket.id} className="p-4 hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedTicket(ticket)}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-2">{ticket.subject}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span>دسته‌بندی: {ticket.category === 'tech' ? 'فنی' : ticket.category === 'financial' ? 'مالی' : 'مشتریان'}</span>
                          <span>تاریخ: {new Date(ticket.created_at).toLocaleDateString('fa-IR')}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                          {ticket.status === 'open' ? 'باز' : 
                           ticket.status === 'in_progress' ? 'در حال بررسی' :
                           ticket.status === 'resolved' ? 'حل شده' : 'بسته'}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                          {ticket.priority === 'urgent' ? 'فوری' :
                           ticket.priority === 'high' ? 'بالا' :
                           ticket.priority === 'medium' ? 'متوسط' : 'پایین'}
                        </span>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* FAQ Tab */}
          {activeTab === 'faq' && (
            <div className="space-y-4">
              {faqs.map(faq => (
                <Card key={faq.id} className="p-4">
                  <div className="mb-2">
                    <span className="text-xs bg-purple-100 text-purple-600 px-2 py-1 rounded-full">
                      {faq.category}
                    </span>
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{faq.question}</h3>
                  <p className="text-gray-600">{faq.answer}</p>
                </Card>
              ))}
            </div>
          )}

          {/* New Ticket Tab */}
          {activeTab === 'new' && (
            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">موضوع</label>
                <input
                  type="text"
                  value={newTicket.subject}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, subject: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="موضوع تیکت را وارد کنید"
                  required
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">دسته‌بندی</label>
                  <select
                    value={newTicket.category}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, category: e.target.value as any }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="tech">پشتیبانی فنی</option>
                    <option value="financial">پشتیبانی مالی</option>
                    <option value="customer">امور مشتریان</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">اولویت</label>
                  <select
                    value={newTicket.priority}
                    onChange={(e) => setNewTicket(prev => ({ ...prev, priority: e.target.value as any }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="low">پایین</option>
                    <option value="medium">متوسط</option>
                    <option value="high">بالا</option>
                    <option value="urgent">فوری</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">توضیحات</label>
                <textarea
                  value={newTicket.description}
                  onChange={(e) => setNewTicket(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={4}
                  placeholder="توضیحات کامل مشکل یا سوال خود را بنویسید"
                  required
                />
              </div>
              
              <button
                type="submit"
                disabled={loadingTickets}
                className="w-full bg-purple-600 text-white py-3 px-6 rounded-xl font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loadingTickets ? 'در حال ایجاد...' : 'ایجاد تیکت'}
              </button>
            </form>
          )}
        </div>

        {/* Ticket Detail Modal */}
        {selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
              <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold">{selectedTicket.subject}</h2>
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 max-h-96 overflow-y-auto space-y-4">
                {selectedTicket.messages.map(message => (
                  <div key={message.id} className={`flex ${message.is_from_user ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs p-3 rounded-xl ${
                      message.is_from_user 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <p>{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.is_from_user ? 'text-purple-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.created_at).toLocaleString('fa-IR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="p-6 border-t">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="پیام خود را بنویسید..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                  <button
                    onClick={() => handleSendMessage(selectedTicket.id)}
                    disabled={!newMessage.trim()}
                    className="bg-purple-600 text-white px-6 py-2 rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ارسال
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
