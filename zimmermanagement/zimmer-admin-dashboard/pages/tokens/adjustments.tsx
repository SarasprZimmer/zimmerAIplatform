'use client';

import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import ProtectedRoute from '../../components/ProtectedRoute';
import { tokenAdjustmentAPI } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import { authClient } from '../../lib/auth-client';

interface TokenAdjustment {
  id: number;
  user_id: number;
  user_name?: string;
  user_automation_id: number;
  automation_name?: string;
  admin_id: number;
  admin_name?: string;
  delta_tokens: number;
  reason: string;
  note?: string;
  related_payment_id?: number;
  created_at: string;
}

interface UserAutomation {
  id: number;
  user_id: number;
  user_name: string;
  automation_id: number;
  automation_name: string;
}

const REASON_LABELS: Record<string, string> = {
  'payment_correction': 'اصلاح پرداخت',
  'promo': 'هدیه/تبلیغاتی',
  'support_fix': 'جبران مشکل',
  'manual': 'دستی'
};

export default function TokenAdjustments() {
  const [adjustments, setAdjustments] = useState<TokenAdjustment[]>([]);
  const [userAutomations, setUserAutomations] = useState<UserAutomation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [selectedUser, setSelectedUser] = useState<number | 'all'>('all');
  const [selectedAutomation, setSelectedAutomation] = useState<number | 'all'>('all');
  const [selectedAdmin, setSelectedAdmin] = useState<number | 'all'>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedReason, setSelectedReason] = useState<string | 'all'>('all');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalAdjustments, setTotalAdjustments] = useState(0);
  
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchUserAutomations();
      fetchAdjustments();
    }
  }, [user, currentPage, selectedUser, selectedAutomation, selectedAdmin, startDate, endDate, selectedReason]);

  const fetchUserAutomations = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/user-automations`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserAutomations(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Error fetching user automations:', err);
    }
  };

  const fetchAdjustments = async () => {
    try {
      setLoading(true);
      
      const filters: any = {
        page: currentPage,
        page_size: pageSize
      };
      
      if (selectedUser !== 'all') {
        filters.user_id = selectedUser;
      }
      
      if (selectedAutomation !== 'all') {
        filters.automation_id = selectedAutomation;
      }
      
      if (selectedAdmin !== 'all') {
        filters.admin_id = selectedAdmin;
      }
      
      if (startDate) {
        filters.start_date = startDate;
      }
      
      if (endDate) {
        filters.end_date = endDate;
      }
      
      const response = await tokenAdjustmentAPI.listAdjustments(filters);
      
      // Enhance adjustments with user and automation names
      const enhancedAdjustments = (response.items || []).map((adjustment: any) => {
        const userAutomation = userAutomations.find(ua => ua.id === adjustment.user_automation_id);
        return {
          ...adjustment,
          user_name: userAutomation?.user_name,
          automation_name: userAutomation?.automation_name
        };
      });
      
      setAdjustments(enhancedAdjustments);
      setTotalAdjustments(response.total || 0);
    } catch (err) {
      console.error('Error fetching adjustments:', err);
      setError('خطا در بارگذاری تاریخچه تنظیمات توکن');
    } finally {
      setLoading(false);
    }
  };

  const getUniqueUsers = () => {
    const users = userAutomations.map(ua => ({
      id: ua.user_id,
      name: ua.user_name
    }));
    return Array.from(new Map(users.map(item => [item.id, item])).values());
  };

  const getUniqueAutomations = () => {
    const automations = userAutomations.map(ua => ({
      id: ua.automation_id,
      name: ua.automation_name
    }));
    return Array.from(new Map(automations.map(item => [item.id, item])).values());
  };

  const getUniqueReasons = () => {
    const reasons = adjustments.map(adj => adj.reason);
    return Array.from(new Set(reasons));
  };

  const totalPages = Math.ceil(totalAdjustments / pageSize);

  const clearFilters = () => {
    setSelectedUser('all');
    setSelectedAutomation('all');
    setSelectedAdmin('all');
    setStartDate('');
    setEndDate('');
    setSelectedReason('all');
    setCurrentPage(1);
  };

  if (loading && adjustments.length === 0) {
    return (
      <ProtectedRoute>
        <Layout title="تاریخچه تنظیمات توکن">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="mr-3 text-gray-600">در حال بارگذاری...</span>
          </div>
        </Layout>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <Layout title="تاریخچه تنظیمات توکن">
          <div className="text-center py-12">
            <div className="text-red-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">خطا در بارگذاری</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchAdjustments}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              تلاش مجدد
            </button>
          </div>
        </Layout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <Layout title="تاریخچه تنظیمات توکن">
        <div className="space-y-6 rtl">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 text-right">تاریخچه تنظیمات توکن</h2>
            <p className="text-gray-600 mt-2 text-right">مشاهده و مدیریت تمام تغییرات موجودی توکن کاربران</p>
          </div>
          
          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* User Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
                  کاربر
                </label>
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="all">همه کاربران</option>
                  {getUniqueUsers().map(user => (
                    <option key={user.id} value={user.id}>
                      {user.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Automation Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
                  اتوماسیون
                </label>
                <select
                  value={selectedAutomation}
                  onChange={(e) => setSelectedAutomation(e.target.value === 'all' ? 'all' : parseInt(e.target.value))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="all">همه اتوماسیون‌ها</option>
                  {getUniqueAutomations().map(automation => (
                    <option key={automation.id} value={automation.id}>
                      {automation.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Reason Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
                  دلیل
                </label>
                <select
                  value={selectedReason}
                  onChange={(e) => setSelectedReason(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="all">همه دلایل</option>
                  {getUniqueReasons().map(reason => (
                    <option key={reason} value={reason}>
                      {REASON_LABELS[reason] || reason}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Date Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
                  بازه زمانی
                </label>
                <div className="flex gap-2">
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>
              
              {/* Clear Filters */}
              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  پاک کردن فیلترها
                </button>
              </div>
            </div>
          </div>

          {/* Adjustments Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 text-right">
                  تنظیمات توکن ({totalAdjustments})
                </h3>
                <button
                  onClick={fetchAdjustments}
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  بروزرسانی
                </button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      تاریخ
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      کاربر
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      اتوماسیون
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      تغییر
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      دلیل
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      توضیحات
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ادمین
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      پرداخت مرتبط
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {adjustments.map((adjustment) => (
                    <tr key={adjustment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {new Date(adjustment.created_at).toLocaleDateString('fa-IR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.user_name || `ID: ${adjustment.user_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.automation_name || `ID: ${adjustment.user_automation_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          adjustment.delta_tokens > 0 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {adjustment.delta_tokens > 0 ? '+' : ''}{adjustment.delta_tokens.toLocaleString()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {REASON_LABELS[adjustment.reason] || adjustment.reason}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                        {adjustment.note || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.admin_name || `ID: ${adjustment.admin_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.related_payment_id ? (
                          <a
                            href={`/payments/${adjustment.related_payment_id}`}
                            className="text-blue-600 hover:text-blue-900 underline"
                          >
                            {adjustment.related_payment_id}
                          </a>
                        ) : (
                          '-'
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-700 text-right">
                    صفحه {currentPage} از {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                      قبلی
                    </button>
                    <button
                      onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                      disabled={currentPage === totalPages}
                      className="px-3 py-1 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                    >
                      بعدی
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
}
