import React, { useState, useEffect, useRef } from 'react';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import api from '../lib/api';

interface AutomationCreationWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface Step1Data {
  name: string;
  description: string;
}

interface Step2Data {
  pricing_type: 'token_per_message' | 'token_per_session';
  price_per_token: number;
}

interface Step3Data {
  api_base_url: string;
  api_provision_url: string;
  api_usage_url: string;
  api_kb_status_url: string;
  api_kb_reset_url: string;
  health_check_url: string;
  dashboard_url: string;
}

interface EndpointValidation {
  url: string;
  status: 'pending' | 'valid' | 'invalid' | 'error';
  message: string;
  lastChecked: Date | null;
}

export default function AutomationCreationWizard({ isOpen, onClose, onSuccess }: AutomationCreationWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [step1Data, setStep1Data] = useState<Step1Data>({ name: '', description: '' });
  const [step2Data, setStep2Data] = useState<Step2Data>({ pricing_type: 'token_per_session', price_per_token: 0 });
  const [step3Data, setStep3Data] = useState<Step3Data>({
    api_base_url: '',
    api_provision_url: '',
    api_usage_url: '',
    api_kb_status_url: '',
    api_kb_reset_url: '',
    health_check_url: '',
    dashboard_url: ''
  });
  
  // Service token generation state - using different variable names to avoid conflicts
  const [showServiceTokenGeneration, setShowServiceTokenGeneration] = useState(false);
  const [serviceToken, setServiceToken] = useState<string | null>(null);
  const [adminPassword, setAdminPassword] = useState('');
  const [serviceTokenConfirmed, setServiceTokenConfirmed] = useState(false);
  const [showServiceToken, setShowServiceToken] = useState(false);
  
  // Endpoint validation state
  const [endpointValidations, setEndpointValidations] = useState<Record<string, EndpointValidation>>({});
  const [validatingEndpoints, setValidatingEndpoints] = useState(false);
  
  // General state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Ref for the password form to prevent any interference
  const passwordFormRef = useRef<HTMLFormElement>(null);

  // Clear any existing form data when component mounts
  useEffect(() => {
    if (isOpen) {
      resetWizard();
    }
  }, [isOpen]);

  // Cleanup sensitive data when component unmounts
  useEffect(() => {
    return () => {
      setAdminPassword('');
      setServiceToken(null);
    };
  }, []);

  const resetWizard = () => {
    setCurrentStep(1);
    setStep1Data({ name: '', description: '' });
    setStep2Data({ pricing_type: 'token_per_session', price_per_token: 0 });
    setStep3Data({
      api_base_url: '',
      api_provision_url: '',
      api_usage_url: '',
      api_kb_status_url: '',
      api_kb_reset_url: '',
      health_check_url: '',
    dashboard_url: ''
    });
    setShowServiceTokenGeneration(false);
    setServiceToken(null);
    setAdminPassword('');
    setServiceTokenConfirmed(false);
    setShowServiceToken(false);
    setEndpointValidations({});
    setValidatingEndpoints(false);
    setError(null);
    setSuccess(null);
  };

  const handleClose = () => {
    // Clear sensitive data immediately
    setAdminPassword('');
    setServiceToken(null);
    resetWizard();
    onClose();
  };

  // Step 1: Generate service token using direct fetch to avoid API client interference
  const handleGenerateServiceToken = async (e?: React.MouseEvent) => {
    // Prevent any default behavior
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    if (!adminPassword.trim()) {
      setError('لطفاً رمز عبور ادمین را وارد کنید');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get the current access token from localStorage
      const accessToken = localStorage.getItem('zimmer_admin_access_token');
      if (!accessToken) {
        throw new Error('No access token found');
      }

      // Use direct fetch with absolute URL to avoid any routing issues
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.zimmerai.com';
      const response = await fetch(`${baseUrl}/api/admin/automations/generate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
          'X-Requested-With': 'XMLHttpRequest' // Prevent CSRF issues
        },
        body: JSON.stringify({ password: adminPassword }),
        credentials: 'include' // Include cookies for CSRF
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate service token');
      }

      const data = await response.json();
      
      // Store the service token in a separate variable
      setServiceToken(data.token);
      setShowServiceTokenGeneration(true);
      setSuccess('توکن سرویس با موفقیت تولید شد');
      
      // Clear the password immediately after successful generation
      setAdminPassword('');
    } catch (error: any) {
      setError(error.message || 'خطا در تولید توکن سرویس');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Validate endpoints
  const validateEndpoint = async (url: string, fieldName: string): Promise<EndpointValidation> => {
    if (!url.trim()) {
      return {
        url,
        status: 'pending',
        message: 'آدرس وارد نشده است',
        lastChecked: null
      };
    }

    try {
      // Test if the endpoint is accessible
      const response = await fetch(url, {
        method: 'HEAD',
        mode: 'no-cors', // This allows us to test CORS endpoints
        cache: 'no-cache'
      });

      return {
        url,
        status: 'valid',
        message: 'آدرس قابل دسترسی است',
        lastChecked: new Date()
      };
    } catch (error) {
      // Try with a simple GET request as fallback
      try {
        const response = await fetch(url, {
          method: 'GET',
          mode: 'no-cors',
          cache: 'no-cache'
        });

        return {
          url,
          status: 'valid',
          message: 'آدرس قابل دسترسی است',
          lastChecked: new Date()
        };
      } catch (fallbackError) {
        return {
          url,
          status: 'invalid',
          message: 'آدرس قابل دسترسی نیست',
          lastChecked: new Date()
        };
      }
    }
  };

  const validateAllEndpoints = async () => {
    setValidatingEndpoints(true);
    setError(null);

    const endpoints = [
      { url: step3Data.api_base_url, field: 'api_base_url' },
      { url: step3Data.api_provision_url, field: 'api_provision_url' },
      { url: step3Data.api_usage_url, field: 'api_usage_url' },
      { url: step3Data.api_kb_status_url, field: 'api_kb_status_url' },
      { url: step3Data.api_kb_reset_url, field: 'api_kb_reset_url' },
      { url: step3Data.health_check_url, field: 'health_check_url' }
    ];

    const validations: Record<string, EndpointValidation> = {};

    for (const endpoint of endpoints) {
      if (endpoint.url.trim()) {
        const validation = await validateEndpoint(endpoint.url, endpoint.field);
        validations[endpoint.field] = validation;
      }
    }

    setEndpointValidations(validations);
    setValidatingEndpoints(false);
  };

  // Check if all required endpoints are valid
  const areAllEndpointsValid = () => {
    const requiredFields = ['api_base_url', 'api_provision_url', 'api_usage_url'];
    return requiredFields.every(field => {
      const validation = endpointValidations[field];
      return validation && validation.status === 'valid';
    });
  };

  // Step 3: Create automation
  const handleCreateAutomation = async () => {
    if (!areAllEndpointsValid()) {
      setError('لطفاً ابتدا تمام آدرس‌های مورد نیاز را تأیید کنید');
      return;
    }

    if (!serviceToken) {
      setError('توکن سرویس یافت نشد. لطفاً دوباره تلاش کنید.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const automationData = {
        ...step1Data,
        ...step2Data,
        ...step3Data,
        status: true,
        service_token: serviceToken
      };

      const response = await api.post('/api/admin/automations', automationData);
      
      setSuccess('اتوماسیون با موفقیت ایجاد شد');
      setTimeout(() => {
        handleClose();
        onSuccess();
      }, 2000);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'خطا در ایجاد اتوماسیون');
    } finally {
      setLoading(false);
    }
  };

  const getValidationIcon = (status: string) => {
    switch (status) {
      case 'valid':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'invalid':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      default:
        return <div className="w-5 h-5 border-2 border-gray-300 rounded-full animate-pulse" />;
    }
  };

  const getValidationColor = (status: string) => {
    switch (status) {
      case 'valid':
        return 'border-green-500 bg-green-50';
      case 'invalid':
        return 'border-red-500 bg-red-50';
      case 'error':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-gray-300';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">ایجاد اتوماسیون جدید</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep >= step
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`w-16 h-1 mx-2 ${
                      currentStep > step ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            {success}
          </div>
        )}

        {/* Step 1: Basic Information & Token Generation */}
        {currentStep === 1 && (
          <form 
            id="automation-wizard-form"
            className="space-y-6" 
            autoComplete="off"
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              return false;
            }}
          >
            <h3 className="text-xl font-semibold">اطلاعات پایه و تولید توکن</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  نام اتوماسیون
                </label>
                <textarea
                  rows={2}
                  required
                  value={step1Data.name}
                  onChange={(e) => setStep1Data({...step1Data, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="نام اتوماسیون خود را وارد کنید"
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="off"
                  spellCheck="false"
                  name="automation-name"
                  data-form-type="other"
                  data-lpignore="true"
                  data-1p-ignore="true"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  توضیحات
                </label>
                <textarea
                  rows={2}
                  required
                  value={step1Data.description}
                  onChange={(e) => setStep1Data({...step1Data, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="توضیحات کوتاه"
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="off"
                  spellCheck="false"
                  name={`automation-description-${Date.now()}`}
                  data-form-type="other"
                  data-lpignore="true"
                  data-1p-ignore="true"
                />
              </div>
            </div>

            {!showServiceTokenGeneration ? (
              <div className="border-t pt-6">
                <h4 className="text-lg font-medium mb-4">تولید توکن سرویس</h4>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mt-0.5 mr-2" />
                    <div className="text-sm text-yellow-800">
                      <p className="font-medium mb-2">هشدار مهم:</p>
                      <ul className="list-disc list-inside space-y-1">
                        <li>این توکن فقط یک بار تولید می‌شود</li>
                        <li>لطفاً آن را در جای امنی ذخیره کنید</li>
                        <li>این توکن را در متغیرهای محیطی اتوماسیون خود قرار دهید</li>
                        <li>بدون این توکن، اتوماسیون شما قادر به اتصال به پلتفرم نخواهد بود</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <form 
                  ref={passwordFormRef}
                  key="service-token-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                  }} 
                  autoComplete="off"
                  className="flex items-center space-x-4"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      e.stopPropagation();
                      handleGenerateServiceToken();
                    }
                  }}
                >
                  {/* Hidden fields to confuse autofill */}
                  <input type="text" style={{display: 'none'}} tabIndex={-1} autoComplete="off" />
                  <input type="password" style={{display: 'none'}} tabIndex={-1} autoComplete="off" />
                  
                  <input
                    type="password"
                    value={adminPassword}
                    onChange={(e) => setAdminPassword(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        e.stopPropagation();
                        handleGenerateServiceToken();
                      }
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="رمز عبور ادمین"
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                    spellCheck="false"
                    name="service-token-admin-password"
                    id="service-token-admin-password"
                    data-form-type="other"
                    data-lpignore="true"
                    data-1p-ignore="true"
                    tabIndex={1}
                  />
                  <button
                    type="button"
                    onClick={handleGenerateServiceToken}
                    disabled={loading || !adminPassword.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'در حال تولید...' : 'تولید توکن'}
                  </button>
                </form>
              </div>
            ) : (
              <div className="border-t pt-6">
                <h4 className="text-lg font-medium mb-4">توکن سرویس تولید شد</h4>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-green-800 mb-2">توکن سرویس شما:</p>
                      <div className="flex items-center space-x-2">
                        <code className="flex-1 bg-white border border-green-300 rounded px-3 py-2 text-sm font-mono">
                          {showServiceToken ? serviceToken : '••••••••••••••••••••••••••••••••'}
                        </code>
                        <button
                          type="button"
                          onClick={() => setShowServiceToken(!showServiceToken)}
                          className="p-2 text-green-600 hover:text-green-800"
                        >
                          {showServiceToken ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <label className="flex items-center space-x-2">
                    <input type="checkbox" id="serviceTokenConfirmed" checked={serviceTokenConfirmed} onChange={(e) => setServiceTokenConfirmed(e.target.checked)} className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
                    <span className="text-sm text-gray-700">من توکن را کپی کرده و در متغیرهای محیطی قرار داده‌ام</span>
                  </label>
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                انصراف
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                disabled={!step1Data.name.trim() || !step1Data.description.trim() || !serviceTokenConfirmed}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                مرحله بعد
              </button>
            </div>
          </form>
        )}

        {/* Step 2: Pricing */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">تنظیمات قیمت‌گذاری</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  روش قیمت‌گذاری
                </label>
                <select
                  value={step2Data.pricing_type}
                  onChange={(e) => setStep2Data({...step2Data, pricing_type: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="token_per_session">به ازای جلسه</option>
                  <option value="token_per_message">به ازای پیام</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  قیمت (تومان)
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={step2Data.price_per_token}
                  onChange={(e) => setStep2Data({...step2Data, price_per_token: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="flex justify-between space-x-4">
              <button
                type="button"
                onClick={() => setCurrentStep(1)}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                مرحله قبل
              </button>
              <button
                type="button"
                onClick={() => setCurrentStep(3)}
                disabled={step2Data.price_per_token <= 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                مرحله بعد
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Endpoints */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">آدرس‌های API</h3>
            
            <div className="space-y-4">
              {[
                { key: 'api_base_url', label: 'آدرس پایه API', required: true },
                { key: 'api_provision_url', label: 'آدرس تأمین سرویس', required: true },
                { key: 'api_usage_url', label: 'آدرس گزارش استفاده', required: true },
                { key: 'api_kb_status_url', label: 'آدرس وضعیت دانش‌نامه', required: false },
                { key: 'api_kb_reset_url', label: 'آدرس بازنشانی دانش‌نامه', required: false },
                { key: 'health_check_url', label: 'آدرس بررسی سلامت', required: false }
              ].map(({ key, label, required }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {label} {required && <span className="text-red-500">*</span>}
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="url"
                      value={step3Data[key as keyof Step3Data]}
                      onChange={(e) => setStep3Data({...step3Data, [key]: e.target.value})}
                      className={`flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        endpointValidations[key] ? getValidationColor(endpointValidations[key].status) : 'border-gray-300'
                      }`}
                      placeholder={`https://example.com/api/${key.replace('api_', '').replace('_url', '')}`}
                    />
                    {endpointValidations[key] && (
                      <div className="flex items-center space-x-2">
                        {getValidationIcon(endpointValidations[key].status)}
                        <span className={`text-xs ${
                          endpointValidations[key].status === 'valid' ? 'text-green-600' :
                          endpointValidations[key].status === 'invalid' ? 'text-red-600' :
                          'text-yellow-600'
                        }`}>
                          {endpointValidations[key].message}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between space-x-4">
              <button
                type="button"
                onClick={() => setCurrentStep(2)}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                مرحله قبل
              </button>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={validateAllEndpoints}
                  disabled={validatingEndpoints}
                  className="px-6 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {validatingEndpoints ? 'در حال بررسی...' : 'بررسی آدرس‌ها'}
                </button>
                <button
                  type="button"
                  onClick={handleCreateAutomation}
                  disabled={loading || !areAllEndpointsValid()}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'در حال ایجاد...' : 'ایجاد اتوماسیون'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
