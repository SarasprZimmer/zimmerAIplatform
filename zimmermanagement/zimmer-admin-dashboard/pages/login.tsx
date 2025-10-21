import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mounted, setMounted] = useState(false)
  const { login, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
    
    if (isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  // Check for expired session message
  const expiredReason = router.query.reason
  const showExpiredMessage = expiredReason === 'expired'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(email, password)
      // Login successful, redirect handled by AuthContext
    } catch (err: any) {
      setError(err.message || 'ایمیل یا رمز عبور اشتباه است')
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) return null

  return (
    <div className="rtl min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Expired Session Message */}
        {showExpiredMessage && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center gap-2">
              <span className="text-red-600">⚠️</span>
              <p className="text-sm text-red-800">نشست شما منقضی شده است. لطفاً دوباره وارد شوید.</p>
            </div>
          </div>
        )}

        <div>
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">ز</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            ورود به حساب کاربری
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            پنل مدیریت زیمر
          </p>

        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                ایمیل
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="ایمیل"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                رمز عبور
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="رمز عبور"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'در حال ورود...' : 'ورود'}
            </button>
          </div>

          <div className="text-center space-y-2">
            <Link
              href="/forgot-password"
              className="font-medium text-blue-600 hover:text-blue-500 block"
            >
              فراموشی رمز عبور
            </Link>
            <p className="text-gray-600 text-sm">
              برای ایجاد حساب کاربری با مدیر سیستم تماس بگیرید
            </p>
          </div>
        </form>
      </div>
    </div>
  )
} 