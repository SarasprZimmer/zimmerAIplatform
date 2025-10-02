import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import DashboardLayout from '@/components/DashboardLayout'
import { Card } from "@/components/ui/Kit"
import { apiFetch } from '@/lib/apiClient'

interface Automation {
  id: number
  name: string
  description: string
  pricing_type: string
  price_per_token: number
  status: string
  is_listed: boolean
  health_status: string
  created_at: string
}

export default function Marketplace(){
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [automations, setAutomations] = useState<Automation[]>([])
  const [loading_automations, setLoadingAutomations] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAutomations();
    }
  }, [isAuthenticated]);

  const fetchAutomations = async () => {
    try {
      setLoadingAutomations(true)
      const response = await apiFetch('/api/optimized/automations/marketplace')
      
      if (response.ok) {
        const data = await response.json()
        setAutomations(data.automations || [])
      } else {
        setError('خطا در بارگذاری اتوماسیون‌ها')
      }
    } catch (err) {
      setError('خطا در بارگذاری اتوماسیون‌ها')
    } finally {
      setLoadingAutomations(false)
    }
  }

  const handleViewDetails = (automationId: number) => {
    router.push(`/automations/${automationId}`)
  }

  const handlePurchase = async (automationId: number) => {
    try {
      setLoadingAutomations(true)
      const response = await apiFetch(`/api/user/automations/${automationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        // Success - redirect to automations page
        router.push('/automations')
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'خطا در اضافه کردن اتوماسیون')
      }
    } catch (err) {
      setError('خطا در اضافه کردن اتوماسیون')
    } finally {
      setLoadingAutomations(false)
    }
  }

  if (loading || loading_automations) {
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">فروشگاه اتوماسیون‌ها</h1>
            <p className="text-gray-600 mt-1">اتوماسیون‌های موجود برای خرید</p>
          </div>
          <div className="text-sm text-gray-500">
            {automations.length} اتوماسیون موجود
          </div>
        </div>

        {/* Error State */}
        {error && (
          <Card>
            <div className="p-6 text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchAutomations}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                تلاش مجدد
              </button>
            </div>
          </Card>
        )}

        {/* Empty State */}
        {!error && automations.length === 0 && (
          <Card>
            <div className="p-6 text-center">
              <p className="text-gray-600 mb-4">هیچ اتوماسیونی در حال حاضر موجود نیست</p>
              <p className="text-sm text-gray-500">لطفاً بعداً مراجعه کنید</p>
            </div>
          </Card>
        )}

        {/* Automations Grid */}
        {!error && automations.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {automations.map((automation) => (
              <Card key={automation.id} className="hover:shadow-lg transition-shadow">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {automation.name}
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2">
                        {automation.description || 'توضیحات این اتوماسیون در حال حاضر در دسترس نیست.'}
                      </p>
                    </div>
                    <span className={`ml-3 px-2 py-1 rounded-full text-xs ${
                      automation.health_status === 'healthy' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {automation.health_status === 'healthy' ? 'سالم' : 'غیرسالم'}
                    </span>
                  </div>

                  {/* Pricing */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">قیمت هر توکن:</span>
                      <span className="font-medium">{automation.price_per_token} ریال</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">توکن‌های رایگان:</span>
                      <span className="font-medium text-green-600">۵ توکن</span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        پاسخگویی خودکار
                      </span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        تلگرام
                      </span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        پایگاه دانش
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-3 space-x-reverse">
                    <button
                      onClick={() => handleViewDetails(automation.id)}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
                    >
                      جزئیات
                    </button>
                    <button
                      onClick={() => handlePurchase(automation.id)}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    >
                      اضافه کردن
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
