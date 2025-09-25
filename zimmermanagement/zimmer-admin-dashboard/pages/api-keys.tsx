import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';
import Layout from '../components/Layout';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface Automation {
  id: number;
  name: string;
}

interface OpenAIKey {
  id: number;
  automation_id: number;
  alias: string;
  status: 'active' | 'disabled' | 'exhausted' | 'error';
  rpm_limit?: number;
  daily_token_limit?: number;
  used_requests_minute: number;
  used_tokens_today: number;
  last_used_at?: string;
  failure_count: number;
  created_at: string;
  updated_at: string;
  masked_key: string;
  automation?: Automation;
}

interface OpenAIKeyCreate {
  automation_id: number;
  alias: string;
  api_key: string;
  rpm_limit?: number;
  daily_token_limit?: number;
  status: 'active' | 'disabled';
}

interface OpenAIKeyUpdate {
  alias?: string;
  api_key?: string;
  rpm_limit?: number;
  daily_token_limit?: number;
  status?: 'active' | 'disabled' | 'exhausted' | 'error';
}

interface TestResponse {
  success: boolean;
  latency_ms?: number;
  model?: string;
  error_message?: string;
}

const APIKeysPage: React.FC = () => {
  const { user } = useAuth();
  const token = authClient.getAccessToken();
  const [keys, setKeys] = useState<OpenAIKey[]>([]);
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedKey, setSelectedKey] = useState<OpenAIKey | null>(null);
  const [filterAutomation, setFilterAutomation] = useState<number | ''>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [testingKey, setTestingKey] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<TestResponse | null>(null);

  // Form states
  const [createForm, setCreateForm] = useState<OpenAIKeyCreate>({
    automation_id: 0,
    alias: '',
    api_key: '',
    status: 'active'
  });

  const [editForm, setEditForm] = useState<OpenAIKeyUpdate>({});

  useEffect(() => {
    fetchKeys();
    fetchAutomations();
  }, [filterAutomation, filterStatus]);

  const fetchKeys = async () => {
    try {
      let url = `${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/list`;
      const params = new URLSearchParams();
      if (filterAutomation) params.append('automation_id', filterAutomation.toString());
      if (filterStatus) params.append('status', filterStatus);
      if (params.toString()) url += `?${params.toString()}`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array before setting it
        if (Array.isArray(data)) {
          setKeys(data);
        } else {
          console.error('Expected array but got:', data);
          setKeys([]);
        }
      } else {
        console.error('Failed to fetch keys:', response.status, response.statusText);
        setKeys([]);
      }
    } catch (error) {
      console.error('Error fetching keys:', error);
      setKeys([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAutomations = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/automations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        // Handle both direct array response and object with automations property
        const automationsArray = Array.isArray(data) ? data : (data?.automations || []);
        setAutomations(automationsArray);
      }
    } catch (error) {
      console.error('Error fetching automations:', error);
    }
  };

  const handleCreate = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(createForm)
      });

      if (response.ok) {
        setShowCreateModal(false);
        setCreateForm({ automation_id: 0, alias: '', api_key: '', status: 'active' });
        fetchKeys();
      } else {
        const error = await response.json();
        alert(error.detail || 'خطا در ایجاد کلید');
      }
    } catch (error) {
      console.error('Error creating key:', error);
      alert('خطا در ایجاد کلید');
    }
  };

  const handleUpdate = async () => {
    if (!selectedKey) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/keys/${selectedKey.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(editForm)
      });

      if (response.ok) {
        setShowEditModal(false);
        setSelectedKey(null);
        setEditForm({});
        fetchKeys();
      } else {
        const error = await response.json();
        alert(error.detail || 'خطا در بروزرسانی کلید');
      }
    } catch (error) {
      console.error('Error updating key:', error);
      alert('خطا در بروزرسانی کلید');
    }
  };

  const handleDelete = async () => {
    if (!selectedKey) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/keys/${selectedKey.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        setShowDeleteModal(false);
        setSelectedKey(null);
        fetchKeys();
      } else {
        alert('خطا در حذف کلید');
      }
    } catch (error) {
      console.error('Error deleting key:', error);
      alert('خطا در حذف کلید');
    }
  };

  const handleStatusUpdate = async (keyId: number, status: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/keys/${keyId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        fetchKeys();
      } else {
        alert('خطا در بروزرسانی وضعیت');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('خطا در بروزرسانی وضعیت');
    }
  };

  const handleTest = async (keyId: number) => {
    setTestingKey(keyId);
    setTestResult(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}/api/admin/keys/${keyId}/test`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      const result: TestResponse = await response.json();
      setTestResult(result);
    } catch (error) {
      console.error('Error testing key:', error);
      setTestResult({ success: false, error_message: 'خطا در تست کلید' });
    } finally {
      setTestingKey(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'disabled':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'exhausted':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'فعال';
      case 'disabled':
        return 'غیرفعال';
      case 'exhausted':
        return 'مصرف شده';
      case 'error':
        return 'خطا';
      default:
        return 'نامشخص';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'disabled':
        return 'bg-red-100 text-red-800';
      case 'exhausted':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const openEditModal = (key: OpenAIKey) => {
    setSelectedKey(key);
    setEditForm({
      alias: key.alias,
      rpm_limit: key.rpm_limit,
      daily_token_limit: key.daily_token_limit,
      status: key.status
    });
    setShowEditModal(true);
  };

  const openDeleteModal = (key: OpenAIKey) => {
    setSelectedKey(key);
    setShowDeleteModal(true);
  };

  if (loading) {
    return (
      <Layout title="کلیدهای OpenAI">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="کلیدهای OpenAI">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">کلیدهای OpenAI</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 font-medium text-lg shadow-lg"
            style={{ minWidth: '200px', justifyContent: 'center' }}
          >
            <PlusIcon className="w-6 h-6" />
            افزودن کلید جدید
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">اتوماسیون</label>
              <select
                value={filterAutomation}
                onChange={(e) => setFilterAutomation(e.target.value ? Number(e.target.value) : '')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">همه اتوماسیون‌ها</option>
                {(automations || []).map(automation => (
                  <option key={automation.id} value={automation.id}>
                    {automation.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">همه وضعیت‌ها</option>
                <option value="active">فعال</option>
                <option value="disabled">غیرفعال</option>
                <option value="exhausted">مصرف شده</option>
                <option value="error">خطا</option>
              </select>
            </div>
          </div>
        </div>

        {/* Keys Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام مستعار
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    اتوماسیون
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    محدودیت RPM
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    سقف روزانه
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    استفاده فعلی
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    آخرین استفاده
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
                {(keys || []).map((key) => (
                  <tr key={key.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{key.alias}</div>
                        <div className="text-sm text-gray-500 font-mono">{key.masked_key}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {automations.find(a => a.id === key.automation_id)?.name || 'نامشخص'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(key.status)}`}>
                        {getStatusIcon(key.status)}
                        <span className="mr-1">{getStatusText(key.status)}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {key.rpm_limit ? `${key.used_requests_minute}/${key.rpm_limit}` : 'نامحدود'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {key.daily_token_limit ? `${key.used_tokens_today.toLocaleString()}/${key.daily_token_limit.toLocaleString()}` : 'نامحدود'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {key.used_requests_minute} درخواست
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {key.last_used_at ? new Date(key.last_used_at).toLocaleString('fa-IR') : 'هیچ‌وقت'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {key.failure_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleTest(key.id)}
                          disabled={testingKey === key.id}
                          className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                        >
                          {testingKey === key.id ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                          ) : (
                            <PlayIcon className="w-5 h-5" />
                          )}
                        </button>
                        <button
                          onClick={() => openEditModal(key)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => openDeleteModal(key)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Test Result */}
        {testResult && (
          <div className={`mt-4 p-4 rounded-lg ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center gap-2">
              {testResult.success ? (
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
              ) : (
                <XCircleIcon className="w-5 h-5 text-red-500" />
              )}
              <span className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                {testResult.success ? 'تست موفق' : 'تست ناموفق'}
              </span>
            </div>
            {testResult.latency_ms && (
              <p className="text-sm text-gray-600 mt-1">زمان پاسخ: {testResult.latency_ms}ms</p>
            )}
            {testResult.model && (
              <p className="text-sm text-gray-600">مدل: {testResult.model}</p>
            )}
            {testResult.error_message && (
              <p className="text-sm text-red-600 mt-1">{testResult.error_message}</p>
            )}
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-lg font-semibold mb-4">افزودن کلید جدید</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">اتوماسیون</label>
                  <select
                    value={createForm.automation_id}
                    onChange={(e) => setCreateForm({...createForm, automation_id: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  >
                    <option value={0}>انتخاب کنید</option>
                    {(automations || []).map(automation => (
                      <option key={automation.id} value={automation.id}>
                        {automation.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">نام مستعار</label>
                  <input
                    type="text"
                    value={createForm.alias}
                    onChange={(e) => setCreateForm({...createForm, alias: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="مثال: travel-key-1"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">کلید API</label>
                  <input
                    type="password"
                    value={createForm.api_key}
                    onChange={(e) => setCreateForm({...createForm, api_key: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="sk-..."
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">محدودیت RPM (اختیاری)</label>
                  <input
                    type="number"
                    value={createForm.rpm_limit || ''}
                    onChange={(e) => setCreateForm({...createForm, rpm_limit: e.target.value ? Number(e.target.value) : undefined})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="60"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">سقف توکن روزانه (اختیاری)</label>
                  <input
                    type="number"
                    value={createForm.daily_token_limit || ''}
                    onChange={(e) => setCreateForm({...createForm, daily_token_limit: e.target.value ? Number(e.target.value) : undefined})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="1000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت</label>
                  <select
                    value={createForm.status}
                    onChange={(e) => setCreateForm({...createForm, status: e.target.value as 'active' | 'disabled'})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="active">فعال</option>
                    <option value="disabled">غیرفعال</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <button
                  onClick={handleCreate}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
                >
                  ایجاد
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  انصراف
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedKey && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-lg font-semibold mb-4">ویرایش کلید</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">نام مستعار</label>
                  <input
                    type="text"
                    value={editForm.alias || ''}
                    onChange={(e) => setEditForm({...editForm, alias: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="مثال: travel-key-1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">کلید API جدید (اختیاری)</label>
                  <input
                    type="password"
                    value={editForm.api_key || ''}
                    onChange={(e) => setEditForm({...editForm, api_key: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="sk-..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">محدودیت RPM (اختیاری)</label>
                  <input
                    type="number"
                    value={editForm.rpm_limit || ''}
                    onChange={(e) => setEditForm({...editForm, rpm_limit: e.target.value ? Number(e.target.value) : undefined})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="60"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">سقف توکن روزانه (اختیاری)</label>
                  <input
                    type="number"
                    value={editForm.daily_token_limit || ''}
                    onChange={(e) => setEditForm({...editForm, daily_token_limit: e.target.value ? Number(e.target.value) : undefined})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="1000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت</label>
                  <select
                    value={editForm.status || ''}
                    onChange={(e) => setEditForm({...editForm, status: e.target.value as any})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    <option value="active">فعال</option>
                    <option value="disabled">غیرفعال</option>
                    <option value="exhausted">مصرف شده</option>
                    <option value="error">خطا</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <button
                  onClick={handleUpdate}
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
                >
                  بروزرسانی
                </button>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  انصراف
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Modal */}
        {showDeleteModal && selectedKey && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-lg font-semibold mb-4">حذف کلید</h2>
              <p className="text-gray-600 mb-6">
                آیا مطمئن هستید که می‌خواهید کلید "{selectedKey.alias}" را حذف کنید؟
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleDelete}
                  className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700"
                >
                  حذف
                </button>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                >
                  انصراف
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default APIKeysPage;
