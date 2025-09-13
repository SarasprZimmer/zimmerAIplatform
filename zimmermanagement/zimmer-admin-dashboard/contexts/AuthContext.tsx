import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/router'
import { authClient } from '@/lib/auth-client'
import { authAPI } from '@/lib/api'
import { startKeepAlive, stopKeepAlive } from '@/lib/keep-alive'

interface User {
  id: number
  name: string
  email: string
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isHydrated, setIsHydrated] = useState(false)

  // Check for expired session message
  const expiredReason = router.query.reason
  const [showExpiredMessage, setShowExpiredMessage] = useState(expiredReason === 'expired')

  // Mark as hydrated after first render
  useEffect(() => {
    setIsHydrated(true)
  }, [])

  // Signup function
  const signup = async (email: string, password: string, name: string) => {
    try {
      const data = await authAPI.signup(email, password, name)
      setUser(data.user)
      router.push('/')
    } catch (error) {
      console.error('Signup error:', error)
      throw error
    }
  }

  // Login function
  const login = async (email: string, password: string) => {
    try {
      const data = await authAPI.login(email, password)
      console.log('Login successful, setting user:', data.user)
      setUser(data.user)
      router.push('/')
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  // Refresh token function
  const refreshToken = async () => {
    try {
      const data = await authAPI.refreshToken()
      setUser(data.user)
    } catch (error) {
      console.error('Token refresh error:', error)
      // Clear auth state on refresh failure
      setUser(null)
      authClient.clearAccessToken()
      throw error
    }
  }

  // Logout function
  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      authClient.clearAccessToken()
      stopKeepAlive()
      router.push('/login')
    }
  }

  // Initialize auth state - ONLY after hydration
  useEffect(() => {
    if (!isHydrated) return; // Don't run until hydrated

    const initializeAuth = async () => {
      try {
        // Check if we have an access token
        if (authClient.isAuthenticated()) {
          // Don't try to validate token on startup - just assume it's valid
          // The user will be redirected to login if the token is invalid
          console.log('Token exists, skipping validation on startup')
          console.log('Current user state:', user)
        } else {
          // No token exists, user needs to login
          console.log('No token found, user needs to login')
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        // Clear invalid state
        setUser(null)
        authClient.clearAccessToken()
      } finally {
        setIsLoading(false)
      }
    }

    initializeAuth()

    // Cleanup keep-alive on unmount
    return () => {
      stopKeepAlive()
    }
  }, [isHydrated, user])

  // Auto-hide expired message after 5 seconds
  useEffect(() => {
    if (showExpiredMessage) {
      const timer = setTimeout(() => {
        setShowExpiredMessage(false)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [showExpiredMessage])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
      
      {/* Expired session banner */}
      {showExpiredMessage && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white p-4 text-center">
          <div className="flex items-center justify-center gap-2">
            <span>⚠️</span>
            <span>نشست شما منقضی شده است. لطفاً دوباره وارد شوید.</span>
            <button 
              onClick={() => setShowExpiredMessage(false)}
              className="text-white hover:text-gray-200 ml-2"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </AuthContext.Provider>
  )
} 