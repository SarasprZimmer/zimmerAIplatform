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

interface DiscountInfo {
  valid: boolean
  code?: string
  percent_off?: number
  amount_before?: number
  amount_discount?: number
  amount_after?: number
  reason?: string
}

export default function TokenPurchasePage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const { id } = router.query
  const [automation, setAutomation] = useState<Automation | null>(null)
  const [userAutomation, setUserAutomation] = useState<UserAutomation | null>(null)
  const [loading_data, setLoadingData] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tokenAmount, setTokenAmount] = useState(100)
  const [discountCode, setDiscountCode] = useState('')
  const [discountInfo, setDiscountInfo] = useState<DiscountInfo | null>(null)
  const [processing, setProcessing] = useState(false)

  // Check if automation uses flat fee pricing
  const isFlatFee = automation?.pricing_type === 'flat_fee'

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  // Set token amount to 1 for flat fee pricing
  useEffect(() => {
    if (isFlatFee) {
      setTokenAmount(1)
    }
  }, [isFlatFee])

  const fetchData = useCallback(async () => {
    try {
      setLoadingData(true)
      setError(null) // Clear any previous errors
      
      // Fetch automation details with cache busting
      const automationResponse = await apiFetch(`/api/automations/${id}?t=${Date.now()}`)
      if (!automationResponse.ok) {
        throw new Error('Automation not found')
      }
      const automationData = await automationResponse.json()
      setAutomation(automationData)

      // Debug logging
      console.log('Automation data:', automationData)
      console.log('user_has_automation:', automationData.user_has_automation)

      // Check if user has this automation
      if (!automationData.user_has_automation) {
        console.log('User does not have automation, showing error')
        setError('شما این اتوماسیون را ندارید. ابتدا آن را خریداری کنید.')
        return
      }

      // Fetch user automation details
      const userAutomationResponse = await apiFetch(`/api/user/automations/${id}`)
      if (userAutomationResponse.ok) {
        const userAutomationData = await userAutomationResponse.json()
        setUserAutomation(userAutomationData.user_automation)
      }

    } catch (err) {
      console.error('Error fetching data:', err)
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

  const handleDiscountValidation = async (code: string) => {
    if (!code || !automation) return
    
    try {
      const response = await apiFetch('/api/discounts/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          automation_id: automation.id,
          amount: automation.price_per_token * tokenAmount
        })
      })
      const data = await response.json()
      setDiscountInfo(data)
    } catch (error) {
      console.error('Discount validation error:', error)
      setDiscountInfo(null)
    }
  }

  const handlePurchase = async () => {
    if (!automation) return
    
    setProcessing(true)
    try {
      const response = await apiFetch('/api/payments/zarinpal/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          automation_id: automation.id,
          tokens: tokenAmount,
          return_path: `/automations/${id}/tokens`,
          discount_code: discountCode || null
        })
      })
      const data = await response.json()
      
      if (data.redirect_url) {
        window.location.href = data.redirect_url
      }
    } catch (error) {
      console.error('Purchase error:', error)
      setError('خطا در پردازش پرداخت')
    } finally {
      setProcessing(false)
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price) + ' ریال'
  }

  const calculateTotal = () => {
    if (!automation) return 0
    const baseAmount = isFlatFee ? automation.price_per_token : automation.price_per_token * tokenAmount
    return discountInfo?.amount_after || baseAmount
  }

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
              <div className="space-x-4 space-x-reverse">
                <button
                  onClick={() => fetchData()}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  🔄 تلاش مجدد
                </button>
                <button
                  onClick={() => router.back()}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                >
                  بازگشت
                </button>
              </div>
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
            <h1 className="text-2xl font-bold text-gray-900">خرید توکن برای {automation.name}</h1>
            <p className="text-gray-600 mt-1">توکن‌های باقی‌مانده: {userAutomation.tokens_remaining}</p>
          </div>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            بازگشت
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Token Purchase Form */}
          <Card>
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">خرید توکن</h2>
              
              <div className="space-y-4">
                {/* Token Amount Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {isFlatFee ? 'نوع خرید' : 'تعداد توکن'}
                  </label>
                  {isFlatFee ? (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800 text-sm">
                        این اتوماسیون از سیستم قیمت‌گذاری ثابت استفاده می‌کند. 
                        شما فقط می‌توانید یک بار خرید کنید.
                      </p>
                      <div className="mt-2 text-lg font-semibold text-blue-900">
                        تعداد توکن: 1
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-2 gap-2 mb-4">
                        {[50, 100, 250, 500, 1000, 2000].map((amount) => (
                          <button
                            key={amount}
                            onClick={() => setTokenAmount(amount)}
                            className={`px-4 py-2 rounded border ${
                              tokenAmount === amount
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                            }`}
                          >
                            {amount.toLocaleString('fa-IR')}
                          </button>
                        ))}
                      </div>
                      <input
                        type="number"
                        min="1"
                        max="100000"
                        value={tokenAmount}
                        onChange={(e) => setTokenAmount(parseInt(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="تعداد توکن مورد نظر را وارد کنید"
                      />
                    </>
                  )}
                </div>

                {/* Discount Code */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    کد تخفیف (اختیاری)
                  </label>
                  <div className="flex space-x-2 space-x-reverse">
                    <input
                      type="text"
                      value={discountCode}
                      onChange={(e) => setDiscountCode(e.target.value)}
                      onBlur={() => handleDiscountValidation(discountCode)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="کد تخفیف خود را وارد کنید"
                    />
                    <button
                      onClick={() => handleDiscountValidation(discountCode)}
                      className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                    >
                      اعمال
                    </button>
                  </div>
                  {discountInfo && (
                    <div className={`mt-2 p-2 rounded text-sm ${
                      discountInfo.valid 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {discountInfo.valid 
                        ? `تخفیف ${discountInfo.percent_off}% اعمال شد`
                        : discountInfo.reason
                      }
                    </div>
                  )}
                </div>

                {/* Price Summary */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="space-y-2">
                    {isFlatFee ? (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">نوع قیمت‌گذاری:</span>
                          <span className="font-medium">ثابت</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">مبلغ کل:</span>
                          <span className="font-medium">{formatPrice(automation.price_per_token)}</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">قیمت هر توکن:</span>
                          <span className="font-medium">{formatPrice(automation.price_per_token)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">تعداد توکن:</span>
                          <span className="font-medium">{tokenAmount.toLocaleString('fa-IR')}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">مبلغ کل:</span>
                          <span className="font-medium">{formatPrice(automation.price_per_token * tokenAmount)}</span>
                        </div>
                      </>
                    )}
                    {discountInfo?.valid && (
                      <>
                        <div className="flex justify-between text-green-600">
                          <span>تخفیف:</span>
                          <span>-{formatPrice(discountInfo.amount_discount || 0)}</span>
                        </div>
                        <div className="border-t pt-2">
                          <div className="flex justify-between text-lg font-semibold">
                            <span>مبلغ نهایی:</span>
                            <span className="text-green-600">{formatPrice(calculateTotal())}</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Purchase Button */}
                <button
                  onClick={handlePurchase}
                  disabled={processing || tokenAmount < 1}
                  className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {processing ? 'در حال پردازش...' : `پرداخت ${formatPrice(calculateTotal())}`}
                </button>
              </div>
            </div>
          </Card>

          {/* Current Status */}
          <Card>
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-4">وضعیت فعلی</h2>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">اتوماسیون:</span>
                  <span className="font-medium">{automation.name}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">توکن‌های باقی‌مانده:</span>
                  <span className="font-medium text-blue-600">{userAutomation.tokens_remaining}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">توکن‌های دمو:</span>
                  <span className="font-medium text-green-600">{userAutomation.demo_tokens}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">وضعیت:</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    userAutomation.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {userAutomation.status === 'active' ? 'فعال' : 'غیرفعال'}
                  </span>
                </div>

                <div className="border-t pt-4">
                  <h3 className="font-medium text-gray-900 mb-2">نحوه استفاده از توکن‌ها</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• هر پیام ارسالی به ربات ۱ توکن مصرف می‌کند</li>
                    <li>• توکن‌های دمو برای تست رایگان هستند</li>
                    <li>• توکن‌های خریداری شده هیچ‌گاه منقضی نمی‌شوند</li>
                    <li>• می‌توانید در هر زمان توکن بیشتری خریداری کنید</li>
                  </ul>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
