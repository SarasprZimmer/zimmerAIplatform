import { useState, useEffect, useCallback } from 'react'
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
  user_has_automation?: boolean
}

export default function AutomationDetailPage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const { id } = router.query
  const [automation, setAutomation] = useState<Automation | null>(null)
  const [loading_automation, setLoadingAutomation] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  const fetchAutomation = useCallback(async () => {
    try {
      setLoadingAutomation(true)
      const response = await apiFetch(`/api/automations/${id}`)
      
      if (response.ok) {
        const data = await response.json()
        setAutomation(data)
      } else {
        setError('اتوماسیون یافت نشد')
      }
    } catch (err) {
      setError('خطا در بارگذاری اتوماسیون')
    } finally {
      setLoadingAutomation(false)
    }
  }, [id])

  useEffect(() => {
    if (id && isAuthenticated) {
      fetchAutomation()
    }
  }, [id, isAuthenticated, fetchAutomation])

  const handlePurchase = async () => {
    try {
      setLoadingAutomation(true)
      const response = await apiFetch(`/api/user/automations/${id}`, {
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
      setLoadingAutomation(false)
    }
  }

  if (loading || loading_automation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6 space-y-4" dir="rtl">
          <div className="text-xl font-semibold text-red-600">خطا</div>
          <Card>
            <div className="text-center py-8">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={() => router.back()}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                بازگشت
              </button>
            </div>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  if (!automation) {
    return (
      <DashboardLayout>
        <div className="p-6 space-y-4" dir="rtl">
          <div className="text-xl font-semibold">اتوماسیون یافت نشد</div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6" dir="rtl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{automation.name}</h1>
            <p className="text-gray-600 mt-1">جزئیات و اطلاعات اتوماسیون</p>
          </div>
          <div className="flex items-center space-x-4 space-x-reverse">
            <span className={`px-3 py-1 rounded-full text-sm ${
              automation.health_status === 'healthy' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {automation.health_status === 'healthy' ? 'سالم' : 'غیرسالم'}
            </span>
            <button
              onClick={() => router.back()}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              بازگشت
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">توضیحات</h2>
                <p className="text-gray-700 leading-relaxed">
                  {automation.description || 'توضیحات این اتوماسیون در حال حاضر در دسترس نیست.'}
                </p>
              </div>
            </Card>

            {/* Features */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">ویژگی‌ها</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700">پاسخگویی خودکار</span>
                  </div>
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700">پشتیبانی از چندین زبان</span>
                  </div>
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700">ادغام با تلگرام</span>
                  </div>
                  <div className="flex items-center space-x-3 space-x-reverse">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700">پایگاه دانش هوشمند</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* How it Works */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">نحوه کار</h2>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4 space-x-reverse">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      1
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">خرید اتوماسیون</h3>
                      <p className="text-gray-600 text-sm">اتوماسیون را خریداری کنید و ۵ توکن رایگان دریافت کنید</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4 space-x-reverse">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      2
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">پیکربندی</h3>
                      <p className="text-gray-600 text-sm">ربات تلگرام خود را پیکربندی کنید</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4 space-x-reverse">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                      3
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">شروع استفاده</h3>
                      <p className="text-gray-600 text-sm">اتوماسیون شروع به کار می‌کند و به کاربران پاسخ می‌دهد</p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Pricing */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">قیمت‌گذاری</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">نوع قیمت‌گذاری:</span>
                    <span className="font-medium">{automation.pricing_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">قیمت هر توکن:</span>
                    <span className="font-medium">{automation.price_per_token} ریال</span>
                  </div>
                  <div className="border-t pt-3">
                    <div className="flex justify-between text-lg font-semibold">
                      <span>توکن‌های رایگان:</span>
                      <span className="text-green-600">۵ توکن</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Purchase Button */}
            <Card>
              <div className="p-6">
                {automation.user_has_automation ? (
                  <div className="space-y-3">
                    <button
                      onClick={() => router.push(`/automations/${id}/dashboard`)}
                      className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      رفتن به داشبورد
                    </button>
                    <button
                      onClick={() => router.push(`/automations/${id}/tokens`)}
                      className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-medium"
                    >
                      خرید توکن
                    </button>
                    <p className="text-sm text-gray-500 text-center">
                      شما این اتوماسیون را دارید. برای مدیریت یا خرید توکن بیشتر کلیک کنید
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <button
                      onClick={handlePurchase}
                      className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      اضافه کردن به اتوماسیون‌های من
                    </button>
                    <p className="text-sm text-gray-500 text-center">
                      با اضافه کردن این اتوماسیون، ۵ توکن رایگان دریافت خواهید کرد
                    </p>
                  </div>
                )}
              </div>
            </Card>

            {/* Status */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">وضعیت</h2>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">وضعیت:</span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      automation.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {automation.status ? 'فعال' : 'غیرفعال'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">در فهرست:</span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      automation.is_listed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {automation.is_listed ? 'بله' : 'خیر'}
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
