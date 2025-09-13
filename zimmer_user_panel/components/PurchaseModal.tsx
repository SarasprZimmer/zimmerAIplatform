'use client'

import { useState } from 'react'
import { XMarkIcon, CreditCardIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface PurchaseModalProps {
  isOpen: boolean
  onClose: () => void
  automation: {
    id: number
    name: string
    price_per_token: number
    pricing_type: string
  }
}

const TOKEN_PACKAGES = [
  { tokens: 10, label: '۱۰ توکن', popular: false },
  { tokens: 50, label: '۵۰ توکن', popular: true },
  { tokens: 100, label: '۱۰۰ توکن', popular: false },
]

export default function PurchaseModal({ isOpen, onClose, automation }: PurchaseModalProps) {
  const [selectedPackage, setSelectedPackage] = useState<number>(50)
  const [customTokens, setCustomTokens] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')

  if (!isOpen) return null

  const handlePackageSelect = (tokens: number) => {
    setSelectedPackage(tokens)
    setCustomTokens('')
  }

  const handleCustomTokensChange = (value: string) => {
    const numValue = parseInt(value)
    if (numValue >= 1 && numValue <= 100000) {
      setCustomTokens(value)
      setSelectedPackage(0)
    } else {
      setCustomTokens('')
    }
  }

  const getSelectedTokens = () => {
    if (customTokens) return parseInt(customTokens)
    return selectedPackage
  }

  const calculateAmount = () => {
    const tokens = getSelectedTokens()
    return tokens * automation.price_per_token
  }

  const formatPrice = (amount: number) => {
    return amount.toLocaleString('fa-IR')
  }

  const handlePurchase = async () => {
    const tokens = getSelectedTokens()
    if (tokens < 1 || tokens > 100000) {
      setError('تعداد توکن باید بین ۱ تا ۱۰۰,۰۰۰ باشد')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/zarinpal/init`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          automation_id: automation.id,
          tokens: tokens,
          return_path: process.env.NEXT_PUBLIC_PAYMENTS_RETURN_ROUTE || '/payment/return'
        }),
      })

      if (!response.ok) {
        throw new Error('خطا در ایجاد پرداخت')
      }

      const data = await response.json()
      
      // Show loading screen before redirect
      const loadingScreen = document.createElement('div')
      loadingScreen.id = 'payment-loading'
      loadingScreen.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'
      loadingScreen.innerHTML = `
        <div class="bg-white rounded-lg p-8 text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">در حال انتقال به درگاه پرداخت</h3>
          <p class="text-gray-500">لطفاً صبر کنید...</p>
        </div>
      `
      document.body.appendChild(loadingScreen)

      // Redirect to Zarinpal
      setTimeout(() => {
        window.location.href = data.redirect_url
      }, 1500)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطای نامشخص')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">خرید توکن</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Automation Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">{automation.name}</h3>
            <p className="text-sm text-gray-600">
              قیمت هر توکن: {formatPrice(automation.price_per_token)} ریال
            </p>
            <p className="text-xs text-gray-500 mt-1">
              نوع قیمت‌گذاری: {automation.pricing_type === 'token_per_session' ? 'به ازای جلسه' : 
                               automation.pricing_type === 'token_per_step' ? 'به ازای مرحله' : 'هزینه ثابت'}
            </p>
          </div>

          {/* Token Packages */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3">انتخاب بسته توکن:</h4>
            <div className="grid grid-cols-3 gap-3 mb-4">
              {TOKEN_PACKAGES.map((pkg) => (
                <button
                  key={pkg.tokens}
                  onClick={() => handlePackageSelect(pkg.tokens)}
                  className={`p-3 border rounded-lg text-center transition-colors ${
                    selectedPackage === pkg.tokens
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  } ${pkg.popular ? 'ring-2 ring-yellow-400' : ''}`}
                >
                  <div className="font-semibold">{pkg.label}</div>
                  {pkg.popular && (
                    <div className="text-xs text-yellow-600 mt-1">محبوب</div>
                  )}
                </button>
              ))}
            </div>

            {/* Custom Tokens */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تعداد سفارشی:
              </label>
              <input
                type="number"
                min="1"
                max="100000"
                value={customTokens}
                onChange={(e) => handleCustomTokensChange(e.target.value)}
                placeholder="تعداد توکن مورد نظر"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                حداقل: ۱ توکن، حداکثر: ۱۰۰,۰۰۰ توکن
              </p>
            </div>
          </div>

          {/* Price Summary */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-gray-700">تعداد توکن:</span>
              <span className="font-semibold">{getSelectedTokens().toLocaleString('fa-IR')}</span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-gray-700">قیمت کل:</span>
              <span className="font-bold text-lg text-blue-600">
                {formatPrice(calculateAmount())} ریال
              </span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              disabled={isLoading}
            >
              انصراف
            </button>
            <button
              onClick={handlePurchase}
              disabled={isLoading || getSelectedTokens() < 1}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  در حال پردازش...
                </>
              ) : (
                <>
                  <CreditCardIcon className="w-4 h-4" />
                  پرداخت با زرین‌پال
                </>
              )}
            </button>
          </div>

          {/* Payment Mode Badge */}
          {process.env.NODE_ENV !== 'production' && (
            <div className="mt-4 text-center">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                حالت آزمایشی
              </span>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
