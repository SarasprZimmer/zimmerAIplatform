'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/router'
import { fetchCsrf } from '@/lib/csrf'
import TwoFADialog from '@/components/TwoFADialog'
import { Toast } from '@/components/Toast'
import { isUnderConstruction } from '@/lib/construction-config'

// Google Login Button Component
function GoogleLoginButton() {
  const api = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com";
  const href = `${api}/api/auth/google/login`;
  
  return (
    <a 
      href={href} 
      className="w-full mt-3 flex justify-center items-center gap-3 rounded-xl border border-gray-200 py-3 px-4 hover:bg-gray-50 transition-colors duration-200"
    >
      <svg width="18" height="18" viewBox="0 0 533.5 544.3">
        <path fill="#4285F4" d="M533.5 278.4c0-18.5-1.5-37.1-4.7-55.3H272.1v104.8h147c-6.1 33.8-25.7 63.7-54.4 82.7v68h87.7c51.5-47.4 81.1-117.4 81.1-200.2z"/>
        <path fill="#34A853" d="M272.1 544.3c73.4 0 135.3-24.1 180.4-65.7l-87.7-68c-24.4 16.6-55.9 26-92.6 26-71 0-131.2-47.9-152.8-112.3H28.9v70.1c46.2 91.9 140.3 149.9 243.2 149.9z"/>
        <path fill="#FBBC05" d="M119.3 324.3c-11.4-33.8-11.4-70.4 0-104.2V150H28.9c-38.6 76.9-38.6 167.5 0 244.4l90.4-70.1z"/>
        <path fill="#EA4335" d="M272.1 107.7c38.8-.6 76.3 14 104.4 40.8l77.7-77.7C405 24.6 337.7-.8 272.1 0 169.2 0 75.1 58 28.9 150l90.4 70.1c21.5-64.5 81.8-112.4 152.8-112.4z"/>
      </svg>
      <span className="text-gray-700 font-medium">ورود با گوگل</span>
    </a>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mounted, setMounted] = useState(false)
  const [toast, setToast] = useState<string | null>(null)
  const [challenge, setChallenge] = useState<string | null>(null)
  const { isAuthenticated, login: authLogin } = useAuth()
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
    
    // 🚧 UNDER CONSTRUCTION: Redirect to maintenance page
    // Change UNDER_CONSTRUCTION in construction-config.ts to false when construction is complete
    if (isUnderConstruction()) {
      router.push('/under-construction')
      return
    }
    
    if (isAuthenticated) {
      router.push('/dashboard')
    }
    // Fetch CSRF token asynchronously without blocking the UI
    fetchCsrf(process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com").catch(err => {
      console.warn('CSRF fetch failed, continuing without CSRF protection:', err);
    });
  }, [isAuthenticated, router])



  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await authLogin(email, password)
      setToast("خوش آمدید!")
      // The AuthContext will handle the redirect to dashboard
    } catch (err: any) {
      if (err?.status === 401 && err?.data?.error === "otp_required" && err?.data?.challenge_token) {
        setChallenge(err.data.challenge_token);
      } else {
        setError(err.message || 'خطا در اتصال به سرور')
      }
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          {/* Expired Session Message */}


          {/* Logo */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-white font-bold text-3xl">Z</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Zimmer AI</h1>
            <p className="text-gray-600">ورود به پنل کاربری</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6">
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
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                رمز عبور
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 bg-gray-50 hover:bg-white"
                required
              />
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-sm text-red-800 text-center">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  در حال ورود...
                </div>
              ) : (
                'ورود'
              )}
            </button>
          </form>

          {/* Google Login Button */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">یا</span>
              </div>
            </div>
            
            <GoogleLoginButton />
          </div>

          {/* Footer */}
          <div className="mt-8 text-center space-y-4">
            <p className="text-sm text-gray-500">
              حساب کاربری ندارید؟{' '}
              <Link href="/signup" className="text-purple-600 hover:text-purple-700 font-medium transition-colors">
                ثبت نام کنید
              </Link>
            </p>
            <p className="text-sm text-gray-500">
              <Link href="/forgot-password" className="text-purple-600 hover:text-purple-700 font-medium transition-colors">
                فراموشی رمز عبور
              </Link>
            </p>
          </div>
        </div>
      </div>
      {challenge && (
        <TwoFADialog
          challengeToken={challenge}
          onSuccess={() => { 
            setChallenge(null); 
            setToast("ورود موفق!"); 
            // The AuthContext will handle the redirect to dashboard
          }}
          onCancel={() => setChallenge(null)}
        />
      )}
      {toast && <Toast msg={toast} onDone={()=>setToast(null)} />}
    </div>
  )
}
