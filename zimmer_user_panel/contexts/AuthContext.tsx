"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import { useRouter } from "next/router"
import ApiClient from "@/lib/api"

interface User {
  id: number
  name: string
  email: string
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  api: ApiClient
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  verifyOtp: (challenge_token: string, otp_code: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [api] = useState(() => new ApiClient())

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (api.isAuthenticated()) {
          const userData = await api.getCurrentUser()
          setUser(userData)
          setIsAuthenticated(true)
        }
      } catch (error) {
        console.log("No valid authentication found")
        api.clearAccessToken()
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [api])

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    try {
      const data = await api.login(email, password)
      setUser(data.user)
      setIsAuthenticated(true)
      // Store user email for mock data detection
      localStorage.setItem('user_email', email)
      router.push("/dashboard")
    } catch (error: any) {
      console.error("Login error:", error)
      // Re-throw the error to let the login page handle 2FA challenges
      throw error
    }
  }, [api, router])

  // Signup function
  const signup = useCallback(async (email: string, password: string, name: string) => {
    try {
      const data = await api.signup(email, password, name)
      setUser(data.user)
      setIsAuthenticated(true)
      router.push("/dashboard")
    } catch (error) {
      console.error("Signup error:", error)
      throw error
    }
  }, [api, router])

  // 2FA verification function
  const verifyOtp = useCallback(async (challenge_token: string, otp_code: string) => {
    try {
      const data = await api.verifyOtp(challenge_token, otp_code)
      setUser(data.user)
      setIsAuthenticated(true)
      // Store user email for mock data detection
      if (data.user?.email) {
        localStorage.setItem('user_email', data.user.email)
      }
      router.push("/dashboard")
    } catch (error) {
      console.error("2FA verification error:", error)
      throw error
    }
  }, [api, router])

  // Logout function
  const logout = useCallback(async () => {
    try {
      await api.logout()
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      setUser(null)
      setIsAuthenticated(false)
      api.clearAccessToken()
      router.push("/login")
    }
  }, [api, router])

  const value: AuthContextType = {
    user,
    isAuthenticated,
    loading,
    api,
    login,
    signup,
    verifyOtp,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
