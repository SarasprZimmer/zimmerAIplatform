'use client';

import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import ProtectedRoute from '../components/ProtectedRoute';
import AdjustTokensModal from '../components/AdjustTokensModal';
import { tokenAdjustmentAPI, adminAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface UserAutomation {
  id: number;
  user_id: number;
  user_name: string;
  user_email: string;
  automation_id: number;
  automation_name: string;
  tokens_remaining: number;
  demo_tokens: number;
  is_demo_active: boolean;
  demo_expired: boolean;
  status: string;
  created_at: string;
}

interface TokenAdjustment {
  id: number;
  user_id: number;
  user_automation_id: number;
  admin_id: number;
  admin_name: string;
  delta_tokens: number;
  reason: string;
  note?: string;
  related_payment_id?: number;
  created_at: string;
}

export default function UserAutomations() {
  const [userAutomations, setUserAutomations] = useState<UserAutomation[]>([]);
  const [tokenAdjustments, setTokenAdjustments] = useState<TokenAdjustment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAutomation, setSelectedAutomation] = useState<number | 'all'>('all');
  const [selectedUser, setSelectedUser] = useState<number | 'all'>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalAdjustments, setTotalAdjustments] = useState(0);
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUserAutomation, setSelectedUserAutomation] = useState<UserAutomation | null>(null);
  
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchUserAutomations();
      fetchTokenAdjustments();
    }
  }, [user, currentPage, selectedAutomation, selectedUser, startDate, endDate]);

  const fetchUserAutomations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await adminAPI.getUserAutomations();
      setUserAutomations(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching user automations:', err);
      setError('Failed to load user automations. Please try again later.');
      setUserAutomations([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTokenAdjustments = async () => {
    try {
      const filters: any = {
        page: currentPage,
        page_size: pageSize
      };
      
      if (selectedAutomation !== 'all') {
        filters.automation_id = selectedAutomation;
      }
      
      if (selectedUser !== 'all') {
        filters.user_id = selectedUser;
      }
      
      if (startDate) {
        filters.start_date = startDate;
      }
      
      if (endDate) {
        filters.end_date = endDate;
      }
      
      const response = await tokenAdjustmentAPI.listAdjustments(filters);
      setTokenAdjustments(response.items || []);
      setTotalAdjustments(response.total || 0);
    } catch (err) {
      console.error('Error fetching token adjustments:', err);
      // Don't set error for adjustments - it's not critical
    }
  };

  const handleTokenAdjustment = (userAutomation: UserAutomation) => {
    setSelectedUserAutomation(userAutomation);
    setIsModalOpen(true);
  };

  const handleAdjustmentSuccess = (newBalance: number) => {
    if (selectedUserAutomation) {
      setUserAutomations(prev => 
        prev.map(ua => 
          ua.id === selectedUserAutomation.id 
            ? { ...ua, tokens_remaining: newBalance }
            : ua
        )
      );
    }
    
    // Refresh adjustments list
    fetchTokenAdjustments();
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const filteredUserAutomations = userAutomations.filter(ua => {
    const matchesSearch = 
      ua.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ua.user_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ua.automation_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesAutomation = selectedAutomation === 'all' || ua.automation_id === selectedAutomation;
    const matchesUser = selectedUser === 'all' || ua.user_id === selectedUser;
    
    return matchesSearch && matchesAutomation && matchesUser;
  });

  const getUniqueAutomations = () => {
    const automations = userAutomations.map(ua => ({
      id: ua.automation_id,
      name: ua.automation_name
    }));
    return Array.from(new Map(automations.map(item => [item.id, item])).values());
  };

  const getUniqueUsers = () => {
    const users = userAutomations.map(ua => ({
      id: ua.user_id,
      name: ua.user_name
    }));
    return Array.from(new Map(users.map(item => [item.id, item])).values());
  };

  const totalPages = Math.ceil(totalAdjustments / pageSize);

  if (loading && userAutomations.length === 0) {
    return (
      <ProtectedRoute>
        <Layout title="مدیریت اتوماسیون‌های کاربران">
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
        <Layout title="مدیریت اتوماسیون‌های کاربران">
          <div className="text-center py-12">
            <div className="text-red-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">خطا در بارگذاری</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchUserAutomations}
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
      <Layout title="مدیریت اتوماسیون‌های کاربران">
        <div className="space-y-6 rtl">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 text-right">مدیریت اتوماسیون‌های کاربران</h2>
            <p className="text-gray-600 mt-2 text-right">مدیریت توکن‌ها و تنظیم موجودی کاربران</p>
          </div>
          
          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2 text-right">
                  جستجو
                </label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={handleSearch}
                  placeholder="جستجو بر اساس نام کاربر یا اتوماسیون..."
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
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
            </div>
          </div>

          {/* User Automations Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 text-right">
                  لیست اتوماسیون‌های کاربران ({filteredUserAutomations.length})
                </h3>
                <button
                  onClick={fetchUserAutomations}
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
                      کاربر
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      اتوماسیون
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      موجودی توکن
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      وضعیت
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      عملیات
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUserAutomations.map((userAutomation) => (
                    <tr key={userAutomation.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900">{userAutomation.user_name}</div>
                          <div className="text-sm text-gray-500">{userAutomation.user_email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {userAutomation.automation_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="text-sm text-gray-900">
                          {userAutomation.tokens_remaining.toLocaleString()} توکن
                        </div>
                        {userAutomation.demo_tokens > 0 && (
                          <div className="text-xs text-gray-500">
                            +{userAutomation.demo_tokens} دمو
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          userAutomation.status === 'active' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {userAutomation.status === 'active' ? 'فعال' : userAutomation.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleTokenAdjustment(userAutomation)}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-md text-xs transition-colors"
                        >
                          تنظیم توکن
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Token Adjustments History */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 text-right">
                تاریخچه تنظیمات توکن ({totalAdjustments})
              </h3>
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
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {tokenAdjustments.map((adjustment) => (
                    <tr key={adjustment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {new Date(adjustment.created_at).toLocaleDateString('fa-IR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.user_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.user_automation_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          adjustment.delta_tokens > 0 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {adjustment.delta_tokens > 0 ? '+' : ''}{adjustment.delta_tokens}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.reason}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                        {adjustment.note || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {adjustment.admin_name}
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

        {/* Token Adjustment Modal */}
        {selectedUserAutomation && (
          <AdjustTokensModal
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              setSelectedUserAutomation(null);
            }}
            userAutomationId={selectedUserAutomation.id}
            automationName={selectedUserAutomation.automation_name}
            userName={selectedUserAutomation.user_name}
            currentBalance={selectedUserAutomation.tokens_remaining}
            onSuccess={handleAdjustmentSuccess}
          />
        )}
      </Layout>
    </ProtectedRoute>
  );
}
