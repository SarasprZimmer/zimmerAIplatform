import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import ApiClient from '@/lib/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [mounted, setMounted] = useState(false)
  const router = useRouter()
  const [api] = useState(() => new ApiClient())

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      await api.forgotPassword(email)
      setSuccess(true)
      setEmail('')
    } catch (err: any) {
      setError(err.message || 'خطا در ارسال ایمیل بازنشانی')
      console.error('Forgot password error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-white font-bold text-3xl">Z</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">فراموشی رمز عبور</h1>
            <p className="text-gray-600">
              ایمیل خود را وارد کنید تا لینک بازنشانی برایتان ارسال شود
            </p>
          </div>

          {/* Success Message */}
          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl mb-6">
              <p className="text-sm text-green-800 text-center">
                اگر ایمیل شما در سیستم ثبت شده باشد، لینک بازنشانی رمز عبور ارسال خواهد شد.
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl mb-6">
              <p className="text-sm text-red-800 text-center">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                ایمیل
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="example@email.com"
                className="w-full px-4 py-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 bg-gray-50 hover:bg-white"
                required
                disabled={loading || success}
              />
            </div>

            <button
              type="submit"
              disabled={loading || success}
              className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  در حال ارسال...
                </div>
              ) : success ? (
                'ایمیل ارسال شد'
              ) : (
                'ارسال لینک بازنشانی'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center space-y-4">
            <p className="text-sm text-gray-500">
              <Link href="/login" className="text-purple-600 hover:text-purple-700 font-medium transition-colors">
                بازگشت به صفحه ورود
              </Link>
            </p>
            {success && (
              <p className="text-sm text-gray-500">
                ایمیل دریافت نکردید؟{' '}
                <button
                  onClick={() => {
                    setSuccess(false)
                    setError('')
                  }}
                  className="text-purple-600 hover:text-purple-700 font-medium transition-colors"
                >
                  تلاش مجدد
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
