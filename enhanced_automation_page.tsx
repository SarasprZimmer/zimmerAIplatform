import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  EyeIcon, 
  KeyIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
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

interface URLValidationResult {
  url: string;
  status: 'valid' | 'invalid' | 'error';
  message: string;
  details?: any;
}

interface ValidationResponse {
  overall_status: 'valid' | 'invalid';
  can_generate_token: boolean;
  results: Record<string, URLValidationResult>;
  summary: string;
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
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [editingAutomation, setEditingAutomation] = useState<Automation | null>(null);
  const [deletingAutomation, setDeletingAutomation] = useState<Automation | null>(null);
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
  
  // Smart Gateway States
  const [validatingUrls, setValidatingUrls] = useState(false);
  const [validationResults, setValidationResults] = useState<ValidationResponse | null>(null);
  const [generatingToken, setGeneratingToken] = useState(false);
  const [generatedToken, setGeneratedToken] = useState<string | null>(null);
  const [showTokenModal, setShowTokenModal] = useState(false);

  useEffect(() => {
    fetchAutomations();
  }, []);

  const fetchAutomations = async () => {
    try {
      const response = await api.get('/admin/automations');
      setAutomations(response.data);
    } catch (error) {
      console.error('Error fetching automations:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateUrls = async () => {
    setValidatingUrls(true);
    try {
      const urls = {
        api_base_url: formData.api_base_url,
        api_provision_url: formData.api_provision_url,
        api_usage_url: formData.api_usage_url,
        api_kb_status_url: formData.api_kb_status_url,
        api_kb_reset_url: formData.api_kb_reset_url
      };

      const response = await api.post('/admin/automations/validate-urls', urls);
      setValidationResults(response.data);
    } catch (error) {
      console.error('Error validating URLs:', error);
      setValidationResults({
        overall_status: 'error',
        can_generate_token: false,
        results: {},
        summary: 'Error validating URLs'
      });
    } finally {
      setValidatingUrls(false);
    }
  };

  const generateServiceToken = async (automationId: number) => {
    setGeneratingToken(true);
    try {
      const response = await api.post(`/admin/automations/${automationId}/generate-service-token`);
      setGeneratedToken(response.data.service_token);
      setShowTokenModal(true);
      fetchAutomations(); // Refresh to show updated token status
    } catch (error) {
      console.error('Error generating service token:', error);
    } finally {
      setGeneratingToken(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingAutomation) {
        await api.put(`/admin/automations/${editingAutomation.id}`, formData);
      } else {
        await api.post('/admin/automations', formData);
      }
      
      setShowForm(false);
      setEditingAutomation(null);
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
      setValidationResults(null);
      fetchAutomations();
    } catch (error) {
      console.error('Error saving automation:', error);
    }
  };

  const handleDelete = async () => {
    if (!deletingAutomation) return;
    
    try {
      await api.delete(`/admin/automations/${deletingAutomation.id}`);
      setShowDeleteConfirm(false);
      setDeletingAutomation(null);
      fetchAutomations();
    } catch (error) {
      console.error('Error deleting automation:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valid':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'invalid':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid':
        return 'text-green-600 bg-green-100';
      case 'invalid':
        return 'text-red-600 bg-red-100';
      case 'error':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">مدیریت اتوماسیون‌ها</h1>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <PlusIcon className="w-5 h-5" />
            افزودن اتوماسیون
          </button>
        </div>

        {/* Smart Gateway URL Validation Section */}
        {showForm && (
          <div className="mb-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">🔍 Smart Gateway - URL Validation</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  آدرس پایه API
                </label>
                <input
                  type="url"
                  value={formData.api_base_url}
                  onChange={(e) => setFormData({...formData, api_base_url: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="https://your-automation.com/api"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  آدرس تدارک (Provision)
                </label>
                <input
                  type="url"
                  value={formData.api_provision_url}
                  onChange={(e) => setFormData({...formData, api_provision_url: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="https://your-automation.com/api/provision"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  آدرس مصرف (Usage)
                </label>
                <input
                  type="url"
                  value={formData.api_usage_url}
                  onChange={(e) => setFormData({...formData, api_usage_url: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="https://your-automation.com/api/usage"
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
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="https://your-automation.com/api/kb/status"
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
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="https://your-automation.com/api/kb/reset"
                />
              </div>
            </div>

            <div className="flex gap-4 mb-4">
              <button
                onClick={validateUrls}
                disabled={validatingUrls}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {validatingUrls ? (
                  <ArrowPathIcon className="w-5 h-5 animate-spin" />
                ) : (
                  <CheckCircleIcon className="w-5 h-5" />
                )}
                {validatingUrls ? 'در حال بررسی...' : 'بررسی URL ها'}
              </button>
            </div>

            {/* Validation Results */}
            {validationResults && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-3">نتایج بررسی:</h3>
                <p className={`mb-4 p-3 rounded-lg ${validationResults.overall_status === 'valid' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {validationResults.summary}
                </p>
                
                <div className="space-y-2">
                  {Object.entries(validationResults.results).map(([urlType, result]) => (
                    <div key={urlType} className="flex items-center gap-3 p-2 bg-white rounded">
                      {getStatusIcon(result.status)}
                      <div className="flex-1">
                        <div className="font-medium">{urlType.replace('_', ' ')}</div>
                        <div className="text-sm text-gray-600">{result.message}</div>
                        {result.details && (
                          <div className="text-xs text-gray-500 mt-1">
                            Status: {result.details.status_code || 'N/A'}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {validationResults.can_generate_token && (
                  <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-lg">
                    ✅ همه URL ها معتبر هستند. می‌توانید توکن سرویس را تولید کنید.
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Automation Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">
              {editingAutomation ? 'ویرایش اتوماسیون' : 'افزودن اتوماسیون جدید'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    نام اتوماسیون
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    قیمت هر توکن (ریال)
                  </label>
                  <input
                    type="number"
                    value={formData.price_per_token}
                    onChange={(e) => setFormData({...formData, price_per_token: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  توضیحات
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نوع قیمت‌گذاری
                </label>
                <select
                  value={formData.pricing_type}
                  onChange={(e) => setFormData({...formData, pricing_type: e.target.value as any})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  {Object.entries(pricingTypeLabels).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.checked})}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">فعال</span>
                </label>
              </div>
              
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={!validationResults?.can_generate_token}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {editingAutomation ? 'به‌روزرسانی' : 'ایجاد اتوماسیون'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingAutomation(null);
                    setValidationResults(null);
                  }}
                  className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
                >
                  انصراف
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Automations List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نوع قیمت‌گذاری
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    قیمت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    توکن سرویس
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {automations.map((automation) => (
                  <tr key={automation.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{automation.name}</div>
                        <div className="text-sm text-gray-500">{automation.description}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {pricingTypeLabels[automation.pricing_type]}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {automation.price_per_token.toLocaleString()} ریال
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        automation.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {automation.status ? 'فعال' : 'غیرفعال'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {automation.has_service_token ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          ✅ موجود
                        </span>
                      ) : (
                        <button
                          onClick={() => generateServiceToken(automation.id)}
                          disabled={generatingToken}
                          className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 hover:bg-blue-200 disabled:opacity-50 flex items-center gap-1"
                        >
                          <KeyIcon className="w-3 h-3" />
                          تولید توکن
                        </button>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
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
                          }}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setDeletingAutomation(automation);
                            setShowDeleteConfirm(true);
                          }}
                          className="text-red-600 hover:text-red-900"
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

        {/* Service Token Modal */}
        {showTokenModal && generatedToken && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
              <h3 className="text-lg font-semibold mb-4">🔑 Service Token Generated</h3>
              
              <div className="bg-gray-100 p-4 rounded-lg mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Token (Copy this to your automation):
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={generatedToken}
                    readOnly
                    className="flex-1 border border-gray-300 rounded px-3 py-2 font-mono text-sm"
                  />
                  <button
                    onClick={() => navigator.clipboard.writeText(generatedToken)}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="bg-yellow-100 p-4 rounded-lg mb-4">
                <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Important for Automation Developer:</h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• Add this token to your automation's environment variables</li>
                  <li>• Verify the X-Zimmer-Service-Token header in incoming requests</li>
                  <li>• Only process requests with valid tokens</li>
                  <li>• Return 401 error for invalid tokens</li>
                </ul>
              </div>

              <div className="flex justify-end gap-4">
                <button
                  onClick={() => {
                    setShowTokenModal(false);
                    setGeneratedToken(null);
                  }}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && deletingAutomation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold mb-4">تأیید حذف</h3>
              <p className="text-gray-600 mb-6">
                آیا مطمئن هستید که می‌خواهید اتوماسیون "{deletingAutomation.name}" را حذف کنید؟
              </p>
              <div className="flex gap-4">
                <button
                  onClick={handleDelete}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  حذف
                </button>
                <button
                  onClick={() => {
                    setShowDeleteConfirm(false);
                    setDeletingAutomation(null);
                  }}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
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
}
