import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
// Removed deprecated authenticatedFetch import
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface BackupLog {
  id: number;
  backup_date: string;
  file_name: string;
  file_size: number;
  status: 'success' | 'failed';
  storage_location: string;
  verified: boolean;
  created_at: string;
}

interface BackupStats {
  total_backups: number;
  successful_backups: number;
  failed_backups: number;
  verified_backups: number;
  last_successful_backup: string | null;
  total_size_bytes: number;
}

const statusConfig = {
  success: { color: 'text-green-600', bg: 'bg-green-100', icon: '🟢', label: 'موفق' },
  failed: { color: 'text-red-600', bg: 'bg-red-100', icon: '🔴', label: 'ناموفق' }
};

export default function Backups() {
  const [backups, setBackups] = useState<BackupLog[]>([]);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    from_date: '',
    to_date: ''
  });
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (user && !isLoading) {
      fetchBackups();
      fetchStats();
    } else if (!user && !isLoading) {
      setLoading(false);
    }
  }, [user, isLoading]);

  const fetchBackups = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status_filter', filters.status);
      if (filters.from_date) params.append('from_date', filters.from_date);
      if (filters.to_date) params.append('to_date', filters.to_date);
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/backups?${params}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در دریافت بکاپ‌ها: ${res.status} ${errorText}`);
      }
      
      const data = await res.json();
      setBackups(data || []);
    } catch (err) {
      console.error('Error fetching backups:', err);
      setError('خطا در بارگذاری بکاپ‌ها.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/backups/stats`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const triggerBackup = async () => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید بکاپ جدید ایجاد کنید؟')) {
      return;
    }
    
    setTriggering(true);
    setError('');
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/backups/trigger`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در ایجاد بکاپ: ${res.status} ${errorText}`);
      }
      
      const data = await res.json();
      showToast(data.message, data.status === 'success' ? 'success' : 'error');
      
      // Refresh data
      setTimeout(() => {
        fetchBackups();
        fetchStats();
      }, 2000);
    } catch (err) {
      console.error('Error triggering backup:', err);
      setError('خطا در ایجاد بکاپ.');
      showToast('خطا در ایجاد بکاپ', 'error');
    } finally {
      setTriggering(false);
    }
  };

  const verifyBackup = async (backupId: number) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/backups/verify/${backupId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در تایید بکاپ: ${res.status} ${errorText}`);
      }
      
      showToast('بکاپ با موفقیت تایید شد', 'success');
      
      // Refresh data
      fetchBackups();
      fetchStats();
    } catch (err) {
      console.error('Error verifying backup:', err);
      showToast('خطا در تایید بکاپ', 'error');
    }
  };

  const cleanupBackups = async () => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید بکاپ‌های قدیمی را پاک کنید؟')) {
      return;
    }
    
    setCleaning(true);
    setError('');
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/backups/cleanup?retention_days=7`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در پاکسازی: ${res.status} ${errorText}`);
      }
      
      const data = await res.json();
      showToast(data.message, 'success');
      
      // Refresh data
      fetchBackups();
      fetchStats();
    } catch (err) {
      console.error('Error cleaning up backups:', err);
      setError('خطا در پاکسازی بکاپ‌ها.');
      showToast('خطا در پاکسازی', 'error');
    } finally {
      setCleaning(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    fetchBackups();
  };

  const showToast = (message: string, type: 'success' | 'error') => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('fa-IR');
    } catch {
      return 'نامشخص';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 بایت';
    const k = 1024;
    const sizes = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusDisplay = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.failed;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        <span className="ml-1">{config.icon}</span>
        {config.label}
      </span>
    );
  };

  if (loading || isLoading) {
    return (
      <Layout title="پشتیبان‌گیری">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="mr-4">در حال بارگذاری...</span>
        </div>
      </Layout>
    );
  }

  if (!user) {
    return (
      <Layout title="پشتیبان‌گیری">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">احراز هویت مورد نیاز</h2>
            <p className="text-gray-600">لطفاً ابتدا وارد شوید.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="پشتیبان‌گیری">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">پشتیبان‌گیری</h1>
            <p className="text-gray-600 mt-1">
              مدیریت بکاپ‌های پایگاه داده و نظارت بر وضعیت آنها
            </p>
          </div>
          <div className="flex items-center space-x-3 space-x-reverse">
            <button
              onClick={cleanupBackups}
              disabled={cleaning}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {cleaning ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  در حال پاکسازی...
                </>
              ) : (
                <>
                  <span className="ml-2">🗑️</span>
                  پاکسازی بکاپ‌های قدیمی
                </>
              )}
            </button>
            <button
              onClick={triggerBackup}
              disabled={triggering}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {triggering ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  در حال ایجاد بکاپ...
                </>
              ) : (
                <>
                  <span className="ml-2">📦</span>
                  ایجاد بکاپ دستی
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-400">⚠️</span>
              </div>
              <div className="mr-3">
                <h3 className="text-sm font-medium text-red-800">خطا</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">📦</span>
                  </div>
                  <div className="mr-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">تعداد کل بکاپ‌ها</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.total_backups}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🟢</span>
                  </div>
                  <div className="mr-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">بکاپ‌های موفق</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.successful_backups}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">✅</span>
                  </div>
                  <div className="mr-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">بکاپ‌های تایید شده</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.verified_backups}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">🔴</span>
                  </div>
                  <div className="mr-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">بکاپ‌های ناموفق</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.failed_backups}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">فیلترها</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">وضعیت</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">همه</option>
                <option value="success">موفق</option>
                <option value="failed">ناموفق</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">از تاریخ</label>
              <input
                type="date"
                value={filters.from_date}
                onChange={(e) => handleFilterChange('from_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">تا تاریخ</label>
              <input
                type="date"
                value={filters.to_date}
                onChange={(e) => handleFilterChange('to_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={applyFilters}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
              >
                اعمال فیلتر
              </button>
            </div>
          </div>
        </div>

        {/* Backups Table */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">لیست بکاپ‌ها</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              تاریخچه کامل بکاپ‌های پایگاه داده
            </p>
          </div>
          
          {backups.length === 0 ? (
            <div className="text-center py-12">
              <span className="text-4xl">📦</span>
              <h3 className="mt-2 text-sm font-medium text-gray-900">هیچ بکاپی یافت نشد</h3>
              <p className="mt-1 text-sm text-gray-500">
                هنوز هیچ بکاپی ایجاد نشده است.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      تاریخ
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      نام فایل
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      وضعیت
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      اندازه فایل
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      محل ذخیره‌سازی
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      تایید
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      عملیات
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {backups.map((backup) => (
                    <tr key={backup.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(backup.backup_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{backup.file_name}</div>
                        <div className="text-sm text-gray-500">ID: {backup.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusDisplay(backup.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatFileSize(backup.file_size)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {backup.storage_location === 'local' ? 'محلی' : backup.storage_location}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {backup.verified ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <span className="ml-1">✅</span>
                            تایید شده
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            <span className="ml-1">⏳</span>
                            تایید نشده
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {!backup.verified && backup.status === 'success' && (
                          <button
                            onClick={() => verifyBackup(backup.id)}
                            className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-md text-xs"
                          >
                            تایید صحت
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
} 