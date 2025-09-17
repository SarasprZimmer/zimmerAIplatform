import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
// Removed deprecated authenticatedFetch import
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface Automation {
  id: number;
  name: string;
  description: string;
  status: boolean;
  api_kb_status_url?: string;
  api_kb_reset_url?: string;
}

interface KBStatus {
  user_id: number;
  name: string;
  kb_health: 'healthy' | 'warning' | 'error';
  last_updated: string;
  backup_status: boolean;
  error_logs: string[];
  supports_reset: boolean;
}

interface KBStatusResponse {
  automation_id: number;
  automation_name: string;
  total_users: number;
  kb_statuses: KBStatus[];
}

interface KBHistoryRecord {
  id: number;
  user_id: number;
  user_name: string;
  automation_id: number;
  automation_name: string;
  kb_health: string;
  backup_status: boolean;
  error_logs: string[] | null;
  timestamp: string;
}

interface KBHistoryStats {
  total_records: number;
  healthy_count: number;
  warning_count: number;
  problematic_count: number;
  backup_count: number;
}

interface ChartDataPoint {
  date: string;
  healthy: number;
  warning: number;
  problematic: number;
  total: number;
}

const healthStatusConfig = {
  healthy: { color: 'text-green-600', bg: 'bg-green-100', icon: '🟢', label: 'سالم' },
  warning: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '🟡', label: 'هشدار' },
  error: { color: 'text-red-600', bg: 'bg-red-100', icon: '🔴', label: 'مشکل‌دار' }
};

export default function KBMonitoring() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [selectedAutomation, setSelectedAutomation] = useState<Automation | null>(null);
  const [kbStatuses, setKbStatuses] = useState<KBStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [selectedErrorLogs, setSelectedErrorLogs] = useState<string[]>([]);
  
  // History tab state
  const [activeTab, setActiveTab] = useState<'realtime' | 'history'>('realtime');
  const [historyRecords, setHistoryRecords] = useState<KBHistoryRecord[]>([]);
  const [historyStats, setHistoryStats] = useState<KBHistoryStats | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    automation_id: '',
    user_id: '',
    from_date: '',
    to_date: ''
  });
  
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (user && !isLoading) {
      fetchAutomations();
    } else if (!user && !isLoading) {
      setLoading(false);
    }
  }, [user, isLoading]);

  useEffect(() => {
    if (selectedAutomation) {
      if (activeTab === 'realtime') {
        fetchKBStatus(selectedAutomation.id);
      } else {
        fetchHistory(1);
        fetchHistoryStats();
        fetchChartData();
      }
    } else {
      setKbStatuses([]);
      setHistoryRecords([]);
    }
  }, [selectedAutomation, activeTab]);

  const fetchAutomations = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/automations`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در دریافت اتوماسیون‌ها: ${res.status} ${errorText}`);
      }
      
      const data = await res.json();
      console.log('Automations API response:', data, 'Type:', typeof data, 'Is Array:', Array.isArray(data));
      // Handle both direct array response and object with automations property
      const automationsArray = Array.isArray(data) ? data : (data?.automations || []);
      setAutomations(automationsArray);
    } catch (err) {
      console.error('Error fetching automations:', err);
      setError('خطا در بارگذاری اتوماسیون‌ها.');
    } finally {
      setLoading(false);
    }
  };

  const fetchKBStatus = async (automationId: number) => {
    setRefreshing(true);
    setError('');
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/kb-status?automation_id=${automationId}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در دریافت وضعیت پایگاه دانش: ${res.status} ${errorText}`);
      }
      
      const data: KBStatusResponse = await res.json();
      setKbStatuses(data.kb_statuses || []);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Error fetching KB status:', err);
      setError('خطا در بارگذاری وضعیت پایگاه دانش.');
    } finally {
      setRefreshing(false);
    }
  };

  const resetUserKB = async (userAutomationId: number, userName: string) => {
    if (!confirm(`آیا مطمئن هستید که می‌خواهید پایگاه دانش کاربر "${userName}" را بازنشانی کنید؟`)) {
      return;
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/kb-reset/${userAutomationId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در بازنشانی پایگاه دانش: ${res.status} ${errorText}`);
      }
      
      showToast('بازنشانی پایگاه دانش با موفقیت انجام شد', 'success');
      // Refresh the status after reset
      if (selectedAutomation) {
        setTimeout(() => {
          fetchKBStatus(selectedAutomation.id);
        }, 2000);
      }
    } catch (err) {
      console.error('Error resetting KB:', err);
      showToast('خطا در بازنشانی پایگاه دانش', 'error');
    }
  };

  const showErrorLogs = (errorLogs: string[]) => {
    setSelectedErrorLogs(errorLogs);
    setShowErrorModal(true);
  };

  // History functions
  const fetchHistory = async (page: number = 1) => {
    if (!selectedAutomation) return;
    
    setHistoryLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams({
        automation_id: selectedAutomation.id.toString(),
        page: page.toString(),
        limit: '20'
      });
      
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.from_date) params.append('from_date', filters.from_date);
      if (filters.to_date) params.append('to_date', filters.to_date);
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/kb-history?${params}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`خطا در دریافت تاریخچه: ${res.status} ${errorText}`);
      }
      
      const data = await res.json();
      setHistoryRecords(data);
      setCurrentPage(page);
      
      // Calculate total pages (assuming 20 records per page)
      setTotalPages(Math.ceil(data.length / 20) || 1);
      
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('خطا در بارگذاری تاریخچه.');
    } finally {
      setHistoryLoading(false);
    }
  };

  const fetchHistoryStats = async () => {
    if (!selectedAutomation) return;
    
    try {
      const params = new URLSearchParams({
        automation_id: selectedAutomation.id.toString()
      });
      
      if (filters.from_date) params.append('from_date', filters.from_date);
      if (filters.to_date) params.append('to_date', filters.to_date);
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/kb-history/stats?${params}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const stats = await res.json();
        setHistoryStats(stats);
      }
    } catch (err) {
      console.error('Error fetching history stats:', err);
    }
  };

  const fetchChartData = async () => {
    if (!selectedAutomation) return;
    
    try {
      const params = new URLSearchParams({
        automation_id: selectedAutomation.id.toString(),
        days: '7'
      });
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://193.162.129.243:8000"}/api/admin/kb-history/chart-data?${params}`, {
        headers: {
          'Authorization': `Bearer ${authClient.getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setChartData(data.chart_data || []);
      }
    } catch (err) {
      console.error('Error fetching chart data:', err);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    setCurrentPage(1);
    fetchHistory(1);
    fetchHistoryStats();
    fetchChartData();
  };

  const exportToCSV = () => {
    if (historyRecords.length === 0) return;
    
    const headers = ['کاربر', 'وضعیت سلامت', 'بکاپ', 'تاریخ', 'خطاها'];
    const csvContent = [
      headers.join(','),
      ...historyRecords.map(record => [
        record.user_name,
        record.kb_health,
        record.backup_status ? 'بله' : 'خیر',
        formatDate(record.timestamp),
        record.error_logs ? record.error_logs.join('; ') : ''
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `kb_history_${selectedAutomation?.name}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

  const getHealthStatusDisplay = (health: string) => {
    const config = healthStatusConfig[health as keyof typeof healthStatusConfig] || healthStatusConfig.error;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        <span className="ml-1">{config.icon}</span>
        {config.label}
      </span>
    );
  };

  const getStatusBadge = (status: boolean) => {
    return status ? (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <span className="ml-1">✅</span>
        فعال
      </span>
    ) : (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <span className="ml-1">❌</span>
        غیرفعال
      </span>
    );
  };

  if (loading || isLoading) {
    return (
      <Layout title="مانیتورینگ پایگاه دانش">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="mr-4">در حال بارگذاری...</span>
        </div>
      </Layout>
    );
  }

  if (!user) {
    return (
      <Layout title="مانیتورینگ پایگاه دانش">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">احراز هویت مورد نیاز</h2>
            <p className="text-gray-600">لطفاً ابتدا وارد شوید.</p>
          </div>
        </div>
      </Layout>
    );
  }

  const healthyCount = kbStatuses.filter(kb => kb.kb_health === 'healthy').length;
  const problematicCount = kbStatuses.filter(kb => kb.kb_health === 'error' || kb.kb_health === 'warning').length;
  const backedUpCount = kbStatuses.filter(kb => kb.backup_status).length;

  return (
    <Layout title="مانیتورینگ پایگاه دانش">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">مانیتورینگ پایگاه دانش</h1>
            <p className="text-gray-600 mt-1">
              وضعیت پایگاه دانش کاربران در اتوماسیون‌های مختلف
            </p>
          </div>
          <div className="flex items-center space-x-3 space-x-reverse">
            {lastRefresh && (
              <span className="text-sm text-gray-500">
                آخرین به‌روزرسانی: {formatDate(lastRefresh.toISOString())}
              </span>
            )}
            {selectedAutomation && (
              <button
                onClick={() => fetchKBStatus(selectedAutomation.id)}
                disabled={refreshing}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {refreshing ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    در حال بروزرسانی...
                  </>
                ) : (
                  <>
                    <span className="ml-2">🔄</span>
                    بروزرسانی
                  </>
                )}
              </button>
            )}
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

        {/* Automation Selector */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">انتخاب اتوماسیون</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(automations || []).map((automation) => (
              <div
                key={automation.id}
                onClick={() => setSelectedAutomation(automation)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedAutomation?.id === automation.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{automation.name}</h4>
                  {getStatusBadge(automation.status)}
                </div>
                <p className="text-sm text-gray-600 mb-2">{automation.description}</p>
                <div className="text-xs text-gray-500">
                  {automation.api_kb_status_url ? '✅ KB Monitoring فعال' : '❌ KB Monitoring غیرفعال'}
                </div>
              </div>
            ))}
          </div>
          {(!automations || automations.length === 0) && (
            <div className="text-center py-8">
              <span className="text-4xl">🤖</span>
              <h3 className="mt-2 text-sm font-medium text-gray-900">هیچ اتوماسیونی یافت نشد</h3>
              <p className="mt-1 text-sm text-gray-500">
                ابتدا اتوماسیون‌ها را در بخش اتوماسیون‌ها ایجاد کنید.
              </p>
            </div>
          )}
        </div>

        {/* Content Tabs */}
        {selectedAutomation && (
          <div className="bg-white shadow rounded-lg">
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 space-x-reverse">
                <button
                  onClick={() => setActiveTab('realtime')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'realtime'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  وضعیت لحظه‌ای
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'history'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  تاریخچه
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'realtime' ? (
                <RealtimeTab 
                  selectedAutomation={selectedAutomation}
                  kbStatuses={kbStatuses}
                  refreshing={refreshing}
                  lastRefresh={lastRefresh}
                  onRefresh={() => fetchKBStatus(selectedAutomation.id)}
                  onReset={resetUserKB}
                  onShowErrors={showErrorLogs}
                  getHealthStatusDisplay={getHealthStatusDisplay}
                  formatDate={formatDate}
                />
              ) : (
                <HistoryTab
                  selectedAutomation={selectedAutomation}
                  historyRecords={historyRecords}
                  historyStats={historyStats}
                  chartData={chartData}
                  historyLoading={historyLoading}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  filters={filters}
                  onFilterChange={handleFilterChange}
                  onApplyFilters={applyFilters}
                  onPageChange={fetchHistory}
                  onExport={exportToCSV}
                  onShowErrors={showErrorLogs}
                  getHealthStatusDisplay={getHealthStatusDisplay}
                  formatDate={formatDate}
                />
              )}
            </div>
          </div>
        )}



        {/* Error Logs Modal */}
        {showErrorModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">خطاهای پایگاه دانش</h3>
                  <button
                    onClick={() => setShowErrorModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="text-2xl">×</span>
                  </button>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {selectedErrorLogs.map((error, index) => (
                    <div key={index} className="mb-2 p-2 bg-red-50 rounded text-sm text-red-800">
                      {error}
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => setShowErrorModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    بستن
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

// Realtime Tab Component
function RealtimeTab({ 
  selectedAutomation, 
  kbStatuses, 
  refreshing, 
  lastRefresh, 
  onRefresh, 
  onReset, 
  onShowErrors, 
  getHealthStatusDisplay, 
  formatDate 
}: {
  selectedAutomation: Automation;
  kbStatuses: KBStatus[];
  refreshing: boolean;
  lastRefresh: Date | null;
  onRefresh: () => void;
  onReset: (userAutomationId: number, userName: string) => void;
  onShowErrors: (errorLogs: string[]) => void;
  getHealthStatusDisplay: (health: string) => JSX.Element;
  formatDate: (dateString: string) => string;
}) {
  const healthyCount = kbStatuses.filter(kb => kb.kb_health === 'healthy').length;
  const problematicCount = kbStatuses.filter(kb => kb.kb_health === 'error' || kb.kb_health === 'warning').length;
  const backedUpCount = kbStatuses.filter(kb => kb.backup_status).length;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">👥</span>
              </div>
              <div className="mr-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">کل کاربران</dt>
                  <dd className="text-lg font-medium text-gray-900">{kbStatuses.length}</dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">سالم</dt>
                  <dd className="text-lg font-medium text-gray-900">{healthyCount}</dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">مشکل دار</dt>
                  <dd className="text-lg font-medium text-gray-900">{problematicCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">💾</span>
              </div>
              <div className="mr-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">پشتیبان‌گیری شده</dt>
                  <dd className="text-lg font-medium text-gray-900">{backedUpCount}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KB Status Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            وضعیت پایگاه دانش - {selectedAutomation.name}
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            جزئیات وضعیت پایگاه دانش کاربران در این اتوماسیون
          </p>
        </div>
        
        {kbStatuses.length === 0 ? (
          <div className="text-center py-12">
            <span className="text-4xl">📊</span>
            <h3 className="mt-2 text-sm font-medium text-gray-900">هیچ پایگاه دانشی یافت نشد</h3>
            <p className="mt-1 text-sm text-gray-500">
              هیچ کاربری با این اتوماسیون یافت نشد.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    کاربر
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت سلامت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    آخرین بروزرسانی
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت بکاپ
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    خطاها
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {kbStatuses.map((kb, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{kb.name}</div>
                      <div className="text-sm text-gray-500">ID: {kb.user_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getHealthStatusDisplay(kb.kb_health)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(kb.last_updated)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {kb.backup_status ? (
                        <span className="text-green-600">بله</span>
                      ) : (
                        <span className="text-red-600">خیر</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {kb.error_logs.length > 0 ? (
                        <button
                          onClick={() => onShowErrors(kb.error_logs)}
                          className="text-xs text-red-600 hover:text-red-800 underline"
                        >
                          مشاهده خطاها ({kb.error_logs.length})
                        </button>
                      ) : (
                        <span className="text-xs text-gray-500">بدون خطا</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {kb.supports_reset && (
                        <button
                          onClick={() => onReset(index + 1, kb.name)}
                          className="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md text-xs"
                        >
                          ریست
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
  );
}

// History Tab Component
function HistoryTab({
  selectedAutomation,
  historyRecords,
  historyStats,
  chartData,
  historyLoading,
  currentPage,
  totalPages,
  filters,
  onFilterChange,
  onApplyFilters,
  onPageChange,
  onExport,
  onShowErrors,
  getHealthStatusDisplay,
  formatDate
}: {
  selectedAutomation: Automation;
  historyRecords: KBHistoryRecord[];
  historyStats: KBHistoryStats | null;
  chartData: ChartDataPoint[];
  historyLoading: boolean;
  currentPage: number;
  totalPages: number;
  filters: { automation_id: string; user_id: string; from_date: string; to_date: string };
  onFilterChange: (key: string, value: string) => void;
  onApplyFilters: () => void;
  onPageChange: (page: number) => void;
  onExport: () => void;
  onShowErrors: (errorLogs: string[]) => void;
  getHealthStatusDisplay: (health: string) => JSX.Element;
  formatDate: (dateString: string) => string;
}) {
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-3">فیلترها</h4>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">کاربر ID</label>
            <input
              type="text"
              value={filters.user_id}
              onChange={(e) => onFilterChange('user_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              placeholder="فیلتر بر اساس کاربر"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">از تاریخ</label>
            <input
              type="date"
              value={filters.from_date}
              onChange={(e) => onFilterChange('from_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">تا تاریخ</label>
            <input
              type="date"
              value={filters.to_date}
              onChange={(e) => onFilterChange('to_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={onApplyFilters}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
            >
              اعمال فیلتر
            </button>
          </div>
        </div>
      </div>

      {/* Stats and Export */}
      <div className="flex justify-between items-center">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {historyStats && (
            <>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">کل رکوردها</div>
                <div className="text-2xl font-bold text-gray-900">{historyStats.total_records}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">سالم</div>
                <div className="text-2xl font-bold text-green-600">{historyStats.healthy_count}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">هشدار</div>
                <div className="text-2xl font-bold text-yellow-600">{historyStats.warning_count}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">مشکل دار</div>
                <div className="text-2xl font-bold text-red-600">{historyStats.problematic_count}</div>
              </div>
            </>
          )}
        </div>
        <button
          onClick={onExport}
          className="bg-green-600 text-white px-4 py-2 rounded-md text-sm hover:bg-green-700"
        >
          📊 خروجی CSV
        </button>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-medium text-gray-900 mb-4">نمودار 7 روز گذشته</h4>
          <div className="h-64 flex items-end justify-between space-x-2 space-x-reverse">
            {chartData.map((point, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div className="w-full bg-gray-200 rounded-t" style={{ height: `${(point.total / Math.max(...chartData.map(p => p.total))) * 200}px` }}>
                  <div className="w-full bg-green-500 rounded-t" style={{ height: `${(point.healthy / point.total) * 100}%` }}></div>
                  <div className="w-full bg-yellow-500" style={{ height: `${(point.warning / point.total) * 100}%` }}></div>
                  <div className="w-full bg-red-500 rounded-b" style={{ height: `${(point.problematic / point.total) * 100}%` }}></div>
                </div>
                <div className="text-xs text-gray-600 mt-2">{point.date}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            تاریخچه پایگاه دانش - {selectedAutomation.name}
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            تاریخچه وضعیت پایگاه دانش کاربران
          </p>
        </div>
        
        {historyLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">در حال بارگذاری...</p>
          </div>
        ) : historyRecords.length === 0 ? (
          <div className="text-center py-12">
            <span className="text-4xl">📊</span>
            <h3 className="mt-2 text-sm font-medium text-gray-900">هیچ رکورد تاریخی یافت نشد</h3>
            <p className="mt-1 text-sm text-gray-500">
              هیچ رکورد تاریخی برای این اتوماسیون یافت نشد.
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      کاربر
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      وضعیت سلامت
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      بکاپ
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      تاریخ
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      خطاها
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {historyRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{record.user_name}</div>
                        <div className="text-sm text-gray-500">ID: {record.user_id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getHealthStatusDisplay(record.kb_health)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {record.backup_status ? (
                          <span className="text-green-600">بله</span>
                        ) : (
                          <span className="text-red-600">خیر</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(record.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {record.error_logs && record.error_logs.length > 0 ? (
                          <button
                            onClick={() => onShowErrors(record.error_logs!)}
                            className="text-xs text-red-600 hover:text-red-800 underline"
                          >
                            مشاهده خطاها ({record.error_logs.length})
                          </button>
                        ) : (
                          <span className="text-xs text-gray-500">بدون خطا</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => onPageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    قبلی
                  </button>
                  <button
                    onClick={() => onPageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    بعدی
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      صفحه <span className="font-medium">{currentPage}</span> از <span className="font-medium">{totalPages}</span>
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      <button
                        onClick={() => onPageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        قبلی
                      </button>
                      <button
                        onClick={() => onPageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        بعدی
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 