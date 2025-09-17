'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import { authClient } from '@/lib/auth-client'
import { authAPI } from '@/lib/api'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, refreshToken } = useAuth()
  const router = useRouter()
  const [authChecking, setAuthChecking] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // If we have an access token, assume it's valid for now
        // The backend will reject requests if the token is invalid
        if (isAuthenticated) {
          console.log('Token exists, assuming valid for now')
          setAuthChecking(false)
          return
        }

        // No token exists, user needs to login
        console.log('No token found, redirecting to login')
        router.push('/login')
      } catch (error) {
        console.error('Auth check error:', error)
        router.push('/login')
      }
    }

    if (!isLoading) {
      checkAuth()
    }
  }, [isLoading, router])

  // Show loading skeleton while checking auth
  if (isLoading || authChecking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال بررسی احراز هویت...</p>
        </div>
      </div>
    )
  }

  // If not authenticated, show loading (will redirect)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال انتقال به صفحه ورود...</p>
        </div>
      </div>
    )
  }

  // User is authenticated, render children
  return <>{children}</>
} 