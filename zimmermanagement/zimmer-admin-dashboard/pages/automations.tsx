import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { PlusIcon, PencilIcon, TrashIcon, EyeIcon, KeyIcon } from '@heroicons/react/24/outline';
import api from '../lib/api';

interface Automation {
  id: number;
  name: string;
  description: string;
  price_per_token: number;
  pricing_type: 'token_per_message' | 'token_per_session';
  status: boolean;
  api_base_url?: string;
  api_provision_url?: string;
  api_usage_url?: string;
  api_kb_status_url?: string;
  api_kb_reset_url?: string;
  service_token_masked?: string;
  has_service_token: boolean;
  created_at: string;
  updated_at: string;
}

interface AutomationFormData {
  name: string;
  description: string;
  price_per_token: number;
  pricing_type: 'token_per_message' | 'token_per_session';
  status: boolean;
  api_base_url: string;
  api_provision_url: string;
  api_usage_url: string;
  api_kb_status_url: string;
  api_kb_reset_url: string;
}

const pricingTypeLabels = {
  token_per_message: 'به ازای پیام',
  token_per_session: 'به ازای جلسه'
};

export default function Automations() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showIntegration, setShowIntegration] = useState(false);
  const [showRotateToken, setShowRotateToken] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [editingAutomation, setEditingAutomation] = useState<Automation | null>(null);
  const [selectedAutomation, setSelectedAutomation] = useState<Automation | null>(null);
  const [formData, setFormData] = useState<AutomationFormData>({
    name: '',
    description: '',
    price_per_token: 0,
    pricing_type: 'token_per_session',
    status: true,
    api_base_url: '',
    api_provision_url: '',
    api_usage_url: '',
    api_kb_status_url: '',
    api_kb_reset_url: ''
  });
  const [newToken, setNewToken] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchAutomations();
  }, []);

  const fetchAutomations = async () => {
    try {
      const response = await api.get('/api/admin/automations');
      // Extract automations array from response data
      const automations = response.data?.automations || response.data || [];
      setAutomations(Array.isArray(automations) ? automations : []);
    } catch (error) {
      console.error('Error fetching automations:', error);
      setAutomations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    try {
      // Validate required fields
      if (!formData.name.trim()) {
        setError('نام اتوماسیون الزامی است');
        return;
      }
      if (!formData.description.trim()) {
        setError('توضیحات الزامی است');
        return;
      }
      if (formData.price_per_token <= 0) {
        setError('قیمت باید بیشتر از صفر باشد');
        return;
      }

      // Ensure all required fields are present and properly formatted
      const submitData = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        price_per_token: Number(formData.price_per_token),
        pricing_type: formData.pricing_type,
        status: Boolean(formData.status),
        api_base_url: formData.api_base_url.trim() || null,
        api_provision_url: formData.api_provision_url.trim() || null,
        api_usage_url: formData.api_usage_url.trim() || null,
        api_kb_status_url: formData.api_kb_status_url.trim() || null,
        api_kb_reset_url: formData.api_kb_reset_url.trim() || null
      };

      console.log('Submitting automation data:', submitData);

      if (editingAutomation) {
        const response = await api.put(`/api/admin/automations/${editingAutomation.id}`, submitData);
        console.log('Update response:', response.data);
        setSuccess('اتوماسیون با موفقیت به‌روزرسانی شد');
      } else {
        const response = await api.post('/api/admin/automations', submitData);
        console.log('Create response:', response.data);
        setSuccess('اتوماسیون با موفقیت ایجاد شد');
      }
      
      setShowForm(false);
      setEditingAutomation(null);
      resetForm();
      fetchAutomations();
    } catch (error: any) {
      console.error('Error saving automation:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        console.error('Error status:', error.response.status);
        setError(`خطا در ذخیره اتوماسیون: ${error.response.data?.detail || error.response.statusText}`);
      } else {
        setError('خطا در ذخیره اتوماسیون. لطفاً دوباره تلاش کنید.');
      }
    }
  };

  const handleGenerateToken = async (id: number) => {
    try {
      const response = await api.post(`/api/admin/automations/${id}/generate-service-token`);
      if (response.data.service_token) {
        // Show token in a modal-like alert with better formatting
        const token = response.data.service_token;
        const message = `🔑 Service Token Generated Successfully!

Token: ${token}

⚠️ IMPORTANT: Save this token securely. It will not be shown again.

📋 Instructions for Automation Developer:
1. Add this token to your automation's environment variables
2. Verify the X-Zimmer-Service-Token header in incoming requests
3. Only process requests with valid tokens
4. Return 401 error for invalid tokens

Environment Variable: AUTOMATION_${id}_SERVICE_TOKEN=${token}`;
        
        alert(message);
        
        // Refresh the automations list to show updated token status
        fetchAutomations();
      }
    } catch (error: any) {
      console.error('Error generating service token:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate service token';
      alert(`❌ Error: ${errorMessage}`);
    }
  };

  const handleDelete = async () => {
    if (!selectedAutomation) return;
    
    try {
      await api.delete(`/api/admin/automations/${selectedAutomation.id}`);
      setShowDeleteConfirm(false);
      setSelectedAutomation(null);
      setSuccess('اتوماسیون با موفقیت حذف شد');
      fetchAutomations();
    } catch (error: any) {
      console.error('Error deleting automation:', error);
      if (error.response) {
        setError(`خطا در حذف اتوماسیون: ${error.response.data?.detail || error.response.statusText}`);
      } else {
        setError('خطا در حذف اتوماسیون. لطفاً دوباره تلاش کنید.');
      }
    }
  };

  const handleRotateToken = async () => {
    if (!selectedAutomation) return;
    
    try {
      const response = await api.post(`/api/admin/automations/${selectedAutomation.id}/rotate-token`);
      setNewToken(response.data.new_token);
      setShowRotateToken(true);
      fetchAutomations();
    } catch (error) {
      console.error('Error rotating token:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price_per_token: 0,
      pricing_type: 'token_per_session',
      status: true,
      api_base_url: '',
      api_provision_url: '',
      api_usage_url: '',
      api_kb_status_url: '',
      api_kb_reset_url: ''
    });
  };

  const openEditForm = (automation: Automation) => {
    setError(null);
    setSuccess(null);
    setEditingAutomation(automation);
    setFormData({
      name: automation.name,
      description: automation.description,
      price_per_token: automation.price_per_token,
      pricing_type: automation.pricing_type,
      status: automation.status,
      api_base_url: automation.api_base_url || '',
      api_provision_url: automation.api_provision_url || '',
      api_usage_url: automation.api_usage_url || '',
      api_kb_status_url: automation.api_kb_status_url || '',
      api_kb_reset_url: automation.api_kb_reset_url || ''
    });
    setShowForm(true);
  };

  const openIntegrationPanel = (automation: Automation) => {
    setSelectedAutomation(automation);
    setShowIntegration(true);
  };

  const filteredAutomations = (automations || []).filter(automation => {
    const matchesSearch = automation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         automation.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && automation.status) ||
                         (statusFilter === 'inactive' && !automation.status);
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <Layout title="مدیریت اتوماسیون‌ها">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="مدیریت اتوماسیون‌ها">
      <div className="space-y-6">
        {/* Global Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <div className="flex justify-between items-center">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        )}
        
        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            <div className="flex justify-between items-center">
              <span>{success}</span>
              <button
                onClick={() => setSuccess(null)}
                className="text-green-500 hover:text-green-700"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">مدیریت اتوماسیون‌ها</h1>
            <p className="text-gray-600">ایجاد و مدیریت اتوماسیون‌های سیستم</p>
          </div>
          <button
            onClick={() => {
              setError(null);
              setSuccess(null);
              setShowForm(true);
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <PlusIcon className="w-5 h-5" />
            افزودن اتوماسیون
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="جستجو در اتوماسیون‌ها..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">همه</option>
              <option value="active">فعال</option>
              <option value="inactive">غیرفعال</option>
            </select>
          </div>
        </div>

        {/* Automations Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    قیمت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    اتصال
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(filteredAutomations || []).map((automation) => (
                  <tr key={automation.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{automation.name}</div>
                        <div className="text-sm text-gray-500">{automation.description}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {automation.price_per_token ? automation.price_per_token.toLocaleString() : '0'} تومان
                      </div>
                      <div className="text-sm text-gray-500">
                        {pricingTypeLabels[automation.pricing_type]}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        automation.status
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {automation.status ? 'فعال' : 'غیرفعال'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {automation.has_service_token ? (
                          <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            <KeyIcon className="w-3 h-3 mr-1" />
                            متصل
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                            غیرمتصل
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleGenerateToken(automation.id)}
                          className="text-green-600 hover:text-green-900"
                          title="تولید توکن سرویس"
                        >
                          <KeyIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openIntegrationPanel(automation)}
                          className="text-blue-600 hover:text-blue-900"
                          title="مشاهده اتصال"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEditForm(automation)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="ویرایش"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedAutomation(automation);
                            setShowDeleteConfirm(true);
                          }}
                          className="text-red-600 hover:text-red-900"
                          title="حذف"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Empty State */}
        {filteredAutomations.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">هیچ اتوماسیونی یافت نشد</div>
            <button
              onClick={() => setShowForm(true)}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              افزودن اولین اتوماسیون
            </button>
          </div>
        )}
      </div>

      {/* Automation Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingAutomation ? 'ویرایش اتوماسیون' : 'افزودن اتوماسیون جدید'}
            </h2>
            
            {/* Error Message */}
            {error && (
              <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {error}
              </div>
            )}
            
            {/* Success Message */}
            {success && (
              <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
                {success}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* General Information */}
              <div className="border-b pb-4">
                <h3 className="text-lg font-semibold mb-3">اطلاعات عمومی</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      نام اتوماسیون
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      قیمت
                    </label>
                    <input
                      type="number"
                      required
                      min="0"
                      step="0.01"
                      value={formData.price_per_token}
                      onChange={(e) => setFormData({...formData, price_per_token: Number(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      نوع قیمت‌گذاری
                    </label>
                    <select
                      value={formData.pricing_type}
                      onChange={(e) => setFormData({...formData, pricing_type: e.target.value as 'token_per_message' | 'token_per_session'})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="token_per_session">به ازای جلسه</option>
                      <option value="token_per_message">به ازای پیام</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      وضعیت
                    </label>
                    <select
                      value={formData.status.toString()}
                      onChange={(e) => setFormData({...formData, status: e.target.value === 'true'})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="true">فعال</option>
                      <option value="false">غیرفعال</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    توضیحات
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Integration Settings */}
              <div>
                <h3 className="text-lg font-semibold mb-3">تنظیمات اتصال</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      آدرس پایه API
                    </label>
                    <input
                      type="url"
                      value={formData.api_base_url}
                      onChange={(e) => setFormData({...formData, api_base_url: e.target.value})}
                      placeholder="https://api.example.com"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        آدرس تدارک
                      </label>
                      <input
                        type="url"
                        value={formData.api_provision_url}
                        onChange={(e) => setFormData({...formData, api_provision_url: e.target.value})}
                        placeholder="/provision"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        آدرس مصرف
                      </label>
                      <input
                        type="url"
                        value={formData.api_usage_url}
                        onChange={(e) => setFormData({...formData, api_usage_url: e.target.value})}
                        placeholder="/usage"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        آدرس وضعیت KB
                      </label>
                      <input
                        type="url"
                        value={formData.api_kb_status_url}
                        onChange={(e) => setFormData({...formData, api_kb_status_url: e.target.value})}
                        placeholder="/kb/status"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        آدرس بازنشانی KB
                      </label>
                      <input
                        type="url"
                        value={formData.api_kb_reset_url}
                        onChange={(e) => setFormData({...formData, api_kb_reset_url: e.target.value})}
                        placeholder="/kb/reset"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingAutomation(null);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
                >
                  انصراف
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingAutomation ? 'ویرایش' : 'افزودن'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Integration Panel Modal */}
      {showIntegration && selectedAutomation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <h2 className="text-xl font-bold mb-4">اطلاعات اتصال - {selectedAutomation.name}</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">آدرس پایه API</label>
                <input
                  type="text"
                  value={selectedAutomation.api_base_url || ''}
                  readOnly
                  className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">آدرس تدارک</label>
                  <input
                    type="text"
                    value={selectedAutomation.api_provision_url || ''}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">آدرس مصرف</label>
                  <input
                    type="text"
                    value={selectedAutomation.api_usage_url || ''}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">آدرس وضعیت KB</label>
                  <input
                    type="text"
                    value={selectedAutomation.api_kb_status_url || ''}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">آدرس بازنشانی KB</label>
                  <input
                    type="text"
                    value={selectedAutomation.api_kb_reset_url || ''}
                    readOnly
                    className="w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">توکن سرویس</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={selectedAutomation.service_token_masked || 'توکن تنظیم نشده'}
                    readOnly
                    className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded-lg"
                  />
                  <button
                    onClick={handleRotateToken}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                  >
                    <KeyIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowIntegration(false)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                بستن
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rotate Token Modal */}
      {showRotateToken && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">توکن جدید</h2>
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                توکن جدید ایجاد شد. این توکن فقط یک بار نمایش داده می‌شود:
              </p>
              <div className="bg-gray-100 p-3 rounded-lg">
                <code className="text-sm break-all">{newToken}</code>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(newToken);
                  alert('توکن کپی شد!');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                کپی
              </button>
              <button
                onClick={() => setShowRotateToken(false)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                بستن
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && selectedAutomation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">تأیید حذف</h2>
            <p className="text-gray-600 mb-6">
              آیا از حذف اتوماسیون "{selectedAutomation.name}" اطمینان دارید؟
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
              >
                انصراف
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                حذف
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}