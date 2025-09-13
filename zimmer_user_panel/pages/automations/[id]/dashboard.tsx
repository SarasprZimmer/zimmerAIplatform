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
}

interface UserAutomation {
  id: number
  tokens_remaining: number
  demo_tokens: number
  is_demo_active: boolean
  demo_expired: boolean
  status: string
}

export default function AutomationDashboardPage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const { id } = router.query
  const [automation, setAutomation] = useState<Automation | null>(null)
  const [userAutomation, setUserAutomation] = useState<UserAutomation | null>(null)
  const [loading_data, setLoadingData] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  const fetchData = useCallback(async () => {
    try {
      setLoadingData(true)
      
      // Fetch automation details
      const automationResponse = await apiFetch(`/api/automations/${id}`)
      if (!automationResponse.ok) {
        throw new Error('Automation not found')
      }
      const automationData = await automationResponse.json()
      setAutomation(automationData)

      // Check if user has this automation
      if (!automationData.user_has_automation) {
        setError('شما این اتوماسیون را ندارید. ابتدا آن را اضافه کنید.')
        return
      }

      // Fetch user automation details
      const userAutomationResponse = await apiFetch(`/api/user/automations/${id}`)
      if (userAutomationResponse.ok) {
        const userAutomationData = await userAutomationResponse.json()
        setUserAutomation(userAutomationData.user_automation)
      }

    } catch (err) {
      setError('خطا در بارگذاری اطلاعات')
    } finally {
      setLoadingData(false)
    }
  }, [id])

  useEffect(() => {
    if (id && isAuthenticated) {
      fetchData()
    }
  }, [id, isAuthenticated, fetchData])

  if (loading || loading_data) {
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

  if (!automation || !userAutomation) {
    return (
      <DashboardLayout>
        <div className="p-6 space-y-4" dir="rtl">
          <div className="text-xl font-semibold">اطلاعات یافت نشد</div>
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
            <h1 className="text-2xl font-bold text-gray-900">داشبورد {automation.name}</h1>
            <p className="text-gray-600 mt-1">مدیریت و کنترل اتوماسیون شما</p>
          </div>
          <div className="flex items-center space-x-4 space-x-reverse">
            <button
              onClick={() => router.push(`/automations/${id}/tokens`)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              خرید توکن
            </button>
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
            {/* Token Status */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">وضعیت توکن‌ها</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{userAutomation.tokens_remaining}</div>
                    <div className="text-sm text-gray-600">توکن‌های باقی‌مانده</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{userAutomation.demo_tokens}</div>
                    <div className="text-sm text-gray-600">توکن‌های دمو</div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Quick Actions */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">عملیات سریع</h2>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => router.push(`/automations/${id}/tokens`)}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-center"
                  >
                    <div className="text-lg font-medium text-gray-900">خرید توکن</div>
                    <div className="text-sm text-gray-600">افزایش توکن‌های خود</div>
                  </button>
                  <button
                    onClick={() => router.push('/automations')}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 text-center"
                  >
                    <div className="text-lg font-medium text-gray-900">اتوماسیون‌های من</div>
                    <div className="text-sm text-gray-600">مشاهده همه اتوماسیون‌ها</div>
                  </button>
                </div>
              </div>
            </Card>

            {/* Usage Instructions */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">نحوه استفاده</h2>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3 space-x-reverse">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">1</div>
                    <div>
                      <div className="font-medium">اتصال ربات تلگرام</div>
                      <div className="text-sm text-gray-600">ربات را به کانال یا گروه خود اضافه کنید</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 space-x-reverse">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">2</div>
                    <div>
                      <div className="font-medium">شروع گفتگو</div>
                      <div className="text-sm text-gray-600">پیام ارسال کنید تا ربات پاسخ دهد</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 space-x-reverse">
                    <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">3</div>
                    <div>
                      <div className="font-medium">مصرف توکن</div>
                      <div className="text-sm text-gray-600">هر پیام ۱ توکن مصرف می‌کند</div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Automation Info */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">اطلاعات اتوماسیون</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">نام:</span>
                    <span className="font-medium">{automation.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">وضعیت:</span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      userAutomation.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {userAutomation.status === 'active' ? 'فعال' : 'غیرفعال'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">قیمت هر توکن:</span>
                    <span className="font-medium">{automation.price_per_token} ریال</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Support */}
            <Card>
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">پشتیبانی</h2>
                <div className="space-y-3">
                  <button
                    onClick={() => router.push('/support')}
                    className="w-full p-3 text-left border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <div className="font-medium">تماس با پشتیبانی</div>
                    <div className="text-sm text-gray-600">درخواست کمک و راهنمایی</div>
                  </button>
                  <button
                    onClick={() => router.push('/automations')}
                    className="w-full p-3 text-left border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <div className="font-medium">بازگشت به لیست</div>
                    <div className="text-sm text-gray-600">مشاهده همه اتوماسیون‌ها</div>
                  </button>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
