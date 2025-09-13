import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import DashboardLayout from '@/components/DashboardLayout'
import { Card } from "@/components/ui/Kit"
import { apiFetch } from '@/lib/apiClient'

interface PaymentResult {
  payment_id: number
  status: string
  ref_id?: string
  message: string
}

export default function PaymentReturnPage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()
  const { payment_id, Authority, Status } = router.query
  const [paymentResult, setPaymentResult] = useState<PaymentResult | null>(null)
  const [loading_payment, setLoadingPayment] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  const verifyPayment = useCallback(async () => {
    try {
      setLoadingPayment(true)
      
      const response = await apiFetch(
        `/api/payments/zarinpal/callback?payment_id=${payment_id}&Authority=${Authority}&Status=${Status}`
      )
      
      if (response.ok) {
        const result = await response.json()
        setPaymentResult(result)
      } else {
        setError('خطا در تایید پرداخت')
      }
    } catch (err) {
      setError('خطا در تایید پرداخت')
    } finally {
      setLoadingPayment(false)
    }
  }, [payment_id, Authority, Status])

  useEffect(() => {
    if (payment_id && Authority && Status && isAuthenticated) {
      verifyPayment()
    }
  }, [payment_id, Authority, Status, isAuthenticated, verifyPayment])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'text-green-600'
      case 'failed':
        return 'text-red-600'
      case 'canceled':
        return 'text-yellow-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'succeeded':
        return 'پرداخت موفق'
      case 'failed':
        return 'پرداخت ناموفق'
      case 'canceled':
        return 'پرداخت لغو شد'
      default:
        return 'وضعیت نامشخص'
    }
  }

  if (loading || loading_payment) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال تایید پرداخت...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6" dir="rtl">
        <div className="max-w-2xl mx-auto">
          <Card>
            <div className="p-8 text-center">
              {error ? (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <h1 className="text-2xl font-bold text-red-600">خطا در پرداخت</h1>
                  <p className="text-gray-600">{error}</p>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    بازگشت به داشبورد
                  </button>
                </div>
              ) : paymentResult ? (
                <div className="space-y-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto ${
                    paymentResult.status === 'succeeded' 
                      ? 'bg-green-100' 
                      : paymentResult.status === 'failed'
                      ? 'bg-red-100'
                      : 'bg-yellow-100'
                  }`}>
                    {paymentResult.status === 'succeeded' ? (
                      <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </div>
                  
                  <h1 className={`text-2xl font-bold ${getStatusColor(paymentResult.status)}`}>
                    {getStatusText(paymentResult.status)}
                  </h1>
                  
                  <p className="text-gray-600">{paymentResult.message}</p>
                  
                  {paymentResult.ref_id && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">شماره پیگیری:</p>
                      <p className="font-mono text-lg font-semibold">{paymentResult.ref_id}</p>
                    </div>
                  )}
                  
                  <div className="flex space-x-4 space-x-reverse justify-center">
                    <button
                      onClick={() => router.push('/dashboard')}
                      className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      بازگشت به داشبورد
                    </button>
                    {paymentResult.status === 'succeeded' && (
                      <button
                        onClick={() => router.push('/automations')}
                        className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        مشاهده اتوماسیون‌ها
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
                  </div>
                  <h1 className="text-2xl font-bold text-gray-600">در حال پردازش...</h1>
                  <p className="text-gray-600">لطفاً صبر کنید</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
