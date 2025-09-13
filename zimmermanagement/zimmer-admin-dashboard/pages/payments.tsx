import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import PaymentTable from '../components/PaymentTable';
import { adminAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { TableSkeleton } from '../components/LoadingSkeletons';
import { toast } from '../components/Toast';

interface PaymentRecord {
  id: number;
  user_name: string;
  amount: number;
  tokens_purchased: number;
  date: string;
  method: string;
  status: string;
  transaction_id: string;
  automation_id?: number;
  automation_name?: string;
}

interface Automation {
  id: number;
  name: string;
}

export default function Payments() {
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [allPayments, setAllPayments] = useState<PaymentRecord[]>([]);
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterLoading, setFilterLoading] = useState(false);
  
  // Filter states
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [statusFilter, setStatusFilter] = useState('');
  const [automationFilter, setAutomationFilter] = useState('');
  
  // Calculated totals
  const [filteredTotalAmount, setFilteredTotalAmount] = useState<number>(0);
  const [filteredTotalTokens, setFilteredTotalTokens] = useState<number>(0);
  
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchPayments();
      fetchAutomations();
    }
    // eslint-disable-next-line
  }, [user]);

  useEffect(() => {
    applyFilters();
  }, [allPayments, dateRange, statusFilter, automationFilter]);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      if (!user) return;
      const data = await adminAPI.getPayments();
      
      // Sort by newest first
      const sorted = Array.isArray(data.payments) ? data.payments.sort((a: PaymentRecord, b: PaymentRecord) => new Date(b.date).getTime() - new Date(a.date).getTime()) : [];
      setAllPayments(sorted);
      setPayments(sorted);
    } catch (err) {
      console.error('Error fetching payments:', err);
      setAllPayments([]);
      setPayments([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAutomations = async () => {
    try {
      const data = await adminAPI.getAutomations();
      setAutomations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching automations:', err);
      setAutomations([]);
    }
  };

  const applyFilters = () => {
    setFilterLoading(true);
    
    let filtered = [...allPayments];

    // Date range filter
    if (dateRange.start) {
      filtered = filtered.filter(payment => 
        new Date(payment.date) >= new Date(dateRange.start)
      );
    }
    if (dateRange.end) {
      filtered = filtered.filter(payment => 
        new Date(payment.date) <= new Date(dateRange.end + 'T23:59:59')
      );
    }

    // Status filter
    if (statusFilter) {
      filtered = filtered.filter(payment => payment.status === statusFilter);
    }

    // Automation filter
    if (automationFilter) {
      filtered = filtered.filter(payment => 
        payment.automation_id === parseInt(automationFilter)
      );
    }

    setPayments(filtered);
    
    // Calculate filtered totals
    const totalAmount = filtered.reduce((sum, payment) => sum + payment.amount, 0);
    const totalTokens = filtered.reduce((sum, payment) => sum + payment.tokens_purchased, 0);
    
    setFilteredTotalAmount(totalAmount);
    setFilteredTotalTokens(totalTokens);
    
    setFilterLoading(false);
  };

  const clearFilters = () => {
    setDateRange({ start: '', end: '' });
    setStatusFilter('');
    setAutomationFilter('');
  };

  const handleViewTokens = (payment: PaymentRecord) => {
    if (payment.automation_id) {
      // Navigate to automation detail page
      window.open(`/automations/${payment.automation_id}`, '_blank');
    } else {
      toast.info('این پرداخت به اتوماسیون خاصی مرتبط نیست');
    }
  };

  const handleReportIssue = async (payment: PaymentRecord) => {
    try {
      // Create a ticket with pre-filled payment information
      const ticketData = {
        subject: `گزارش مشکل پرداخت - تراکنش ${payment.transaction_id}`,
        message: `مشکل در پرداخت زیر گزارش شده است:\n\nشناسه تراکنش: ${payment.transaction_id}\nمبلغ: ${formatCurrency(payment.amount)}\nتاریخ: ${formatDate(payment.date)}\nوضعیت: ${getStatusText(payment.status)}\n\nلطفاً مشکل را بررسی کنید.`,
        importance: 'medium',
        user_id: user?.id
      };

      await adminAPI.createTicket(ticketData);
      toast.success('تیکت گزارش مشکل ایجاد شد');
    } catch (err) {
      console.error('Error creating ticket:', err);
      toast.error('خطا در ایجاد تیکت');
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'موفق';
      case 'failed': return 'ناموفق';
      case 'cancelled': return 'لغو';
      case 'pending': return 'در انتظار';
      default: return status;
    }
  };

  function formatCurrency(amount: number) {
    return amount.toLocaleString('fa-IR') + ' ریال';
  }

  function formatDate(dateStr: string) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fa-IR');
  }

  const hasActiveFilters = dateRange.start || dateRange.end || statusFilter || automationFilter;

  return (
    <Layout title="تاریخچه پرداخت‌ها">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">تاریخچه پرداخت‌ها</h2>
          <p className="text-gray-600 mt-2">مدیریت و پیگیری پرداخت‌های انجام شده</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col lg:flex-row lg:items-end gap-4">
            {/* Date Range */}
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  از تاریخ
                </label>
                <input
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  تا تاریخ
                </label>
                <input
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                وضعیت
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه</option>
                <option value="completed">موفق</option>
                <option value="failed">ناموفق</option>
                <option value="cancelled">لغو</option>
                <option value="pending">در انتظار</option>
              </select>
            </div>

            {/* Automation Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                اتوماسیون
              </label>
              <select
                value={automationFilter}
                onChange={(e) => setAutomationFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه</option>
                {automations.map(automation => (
                  <option key={automation.id} value={automation.id}>
                    {automation.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                پاک کردن فیلترها
              </button>
              <button
                onClick={fetchPayments}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              >
                {loading ? 'در حال بارگذاری...' : 'بروزرسانی'}
              </button>
            </div>
          </div>
        </div>

        {/* Totals */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {formatCurrency(filteredTotalAmount)}
              </div>
              <div className="text-sm text-gray-500">
                {hasActiveFilters ? 'مجموع فیلتر شده' : 'مجموع کل'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {filteredTotalTokens.toLocaleString('fa-IR')}
              </div>
              <div className="text-sm text-gray-500">
                {hasActiveFilters ? 'توکن‌های فیلتر شده' : 'توکن‌های کل'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {payments.length}
              </div>
              <div className="text-sm text-gray-500">
                تعداد تراکنش‌ها
              </div>
            </div>
          </div>
        </div>

        {/* Payment Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">لیست پرداخت‌ها</h3>
          </div>
          <div className="p-6">
            {loading ? (
              <TableSkeleton rows={5} columns={8} />
            ) : filterLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="mr-3 text-gray-600">در حال اعمال فیلترها...</span>
              </div>
            ) : (
              <PaymentTable 
                records={payments} 
                onViewTokens={handleViewTokens}
                onReportIssue={handleReportIssue}
              />
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
} 