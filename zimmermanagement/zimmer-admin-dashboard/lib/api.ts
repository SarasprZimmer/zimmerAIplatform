import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { authClient, redirectToLogin } from './auth-client'
import { toast } from '../components/Toast'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"



// Error message mapping
const ERROR_MESSAGES = {
  400: 'درخواست نامعتبر',
  401: 'نشست منقضی شده است',
  403: 'دسترسی غیرمجاز',
  404: 'منبع مورد نظر یافت نشد',
  409: 'تضاد در داده‌ها',
  422: 'داده‌های ارسالی نامعتبر',
  429: 'تعداد درخواست‌ها زیاد است، کمی بعد تلاش کنید',
  500: 'خطای داخلی سرور',
  502: 'خطای سرور',
  503: 'سرویس در دسترس نیست',
  504: 'زمان انتظار به پایان رسید'
}

// Helper function to extract error message
const extractErrorMessage = (error: AxiosError): string => {
  // Check if response has detail or message
  if (error.response?.data) {
    const data = error.response.data as any
    if (data.detail) {
      return data.detail
    }
    if (data.message) {
      return data.message
    }
    if (data.error) {
      return data.error
    }
  }

  // Fallback to status code message
  const status = error.response?.status
  if (status && ERROR_MESSAGES[status as keyof typeof ERROR_MESSAGES]) {
    return ERROR_MESSAGES[status as keyof typeof ERROR_MESSAGES]
  }

  // Default error message
  return 'خطای غیرمنتظره رخ داده است'
}

// Helper function to show error toast
const showErrorToast = (error: AxiosError) => {
  const message = extractErrorMessage(error)
  toast.error(message)
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Disabled to avoid CORS issues
  timeout: 30000, // 30 second timeout to prevent hanging requests
})

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  (config) => {
    const token = authClient.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - simplified to avoid infinite loops
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    // Just log the error and reject - no automatic token refresh
    console.error('API Error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

// Token Adjustment API Methods
export const tokenAdjustmentAPI = {
  // Get current token balance for a user automation
  getBalance: async (userAutomationId: number) => {
    try {
      const response = await api.get(`/api/admin/tokens/balance/${userAutomationId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Create a new token adjustment
  postTokenAdjust: async (payload: {
    user_automation_id: number
    delta_tokens: number
    reason: string
    note?: string
    related_payment_id?: number
    idempotency_key?: string
  }) => {
    try {
      const response = await api.post('/api/admin/tokens/adjust', payload)
      toast.success('تغییر توکن با موفقیت انجام شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // List token adjustments with filters
  listAdjustments: async (filters: {
    user_id?: number
    automation_id?: number
    admin_id?: number
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  } = {}) => {
    try {
      const response = await api.get('/api/admin/tokens/adjustments', { params: filters })
      return response.data
    } catch (error) {
      throw error
    }
  }
}

// Auth API Methods
export const authAPI = {
  signup: async (email: string, password: string, name: string) => {
    try {
      const response = await api.post('/api/auth/signup', { email, password, name })
      const data = response.data
      authClient.setAccessToken(data.access_token)
      toast.success('ثبت نام با موفقیت انجام شد')
      return {
        user: {
          id: data.user_id,
          email: data.email,
          name: data.name,
          is_admin: false
        },
        access_token: data.access_token
      }
    } catch (error) {
      throw error
    }
  },

  login: async (email: string, password: string) => {
    try {
      console.log('🔐 Attempting login to:', BASE_URL + '/api/auth/login')
      console.log('📧 Email:', email)
      console.log('🔑 Password:', password ? '[HIDDEN]' : '[MISSING]')
      
      const response = await api.post('/api/auth/login', { email, password })
      console.log('✅ Login response received:', response.status)
      
      const data = response.data
      authClient.setAccessToken(data.access_token)
      toast.success('ورود با موفقیت انجام شد')
      return {
        user: {
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          is_admin: data.user.is_admin
        },
        access_token: data.access_token
      }
    } catch (error: any) {
      console.error('❌ Login error details:', error)
      console.error('❌ Error config:', error.config)
      throw error
    }
  },

  logout: async () => {
    try {
      await api.post('/api/auth/logout')
      toast.success('خروج با موفقیت انجام شد')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      authClient.clearAccessToken()
    }
  },

  refreshToken: async () => {
    try {
      const response = await api.post('/api/auth/refresh')
      const data = response.data
      authClient.setAccessToken(data.access_token)
      // Note: refresh endpoint only returns access_token, not user data
      // We'll need to get user data separately if needed
      return {
        user: null, // Refresh doesn't return user data
        access_token: data.access_token
      }
    } catch (error) {
      throw error
    }
  },

  getCurrentUser: async () => {
    // This endpoint doesn't exist in the backend
    // We'll handle user data through the login response instead
    throw new Error('getCurrentUser endpoint not implemented')
  }
}

// Admin API Methods
export const adminAPI = {
  // User management
  getUsers: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/users/managers', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getUser: async (userId: number) => {
    try {
      const response = await api.get(`/api/admin/users/managers/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateUser: async (userId: number, data: any) => {
    try {
      const response = await api.put(`/api/admin/users/managers/${userId}`, data)
      toast.success('اطلاعات کاربر با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  deleteUser: async (userId: number) => {
    try {
      const response = await api.delete(`/api/admin/users/managers/${userId}`)
      toast.success('کاربر با موفقیت غیرفعال شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  createUser: async (userData: any) => {
    try {
      const response = await api.post('/api/admin/users/managers', userData)
      toast.success('کاربر با موفقیت ایجاد شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Automation management
  getAutomations: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/automations', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getUserAutomations: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/user-automations', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getAutomation: async (automationId: number) => {
    try {
      const response = await api.get(`/api/admin/automations/${automationId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateAutomation: async (automationId: number, data: any) => {
    try {
      const response = await api.put(`/api/admin/automations/${automationId}`, data)
      toast.success('اتوماسیون با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Payment management
  getPayments: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/payments', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getPayment: async (paymentId: number) => {
    try {
      const response = await api.get(`/api/admin/payments/${paymentId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Support tickets
  getTickets: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/tickets', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getTicket: async (ticketId: number) => {
    try {
      const response = await api.get(`/api/admin/tickets/${ticketId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateTicket: async (ticketId: number, data: any) => {
    try {
      const response = await api.put(`/api/tickets/${ticketId}`, data)
      toast.success('تیکت با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  deleteTicket: async (ticketId: number) => {
    try {
      await api.delete(`/api/tickets/${ticketId}`)
      toast.success('تیکت با موفقیت حذف شد')
    } catch (error) {
      throw error
    }
  },

  // Usage statistics
  getUsageStats: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/usage', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // System monitoring
  getSystemStatus: async () => {
    try {
      const response = await api.get('/api/admin/system/status')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Backups
  getBackups: async () => {
    try {
      const response = await api.get('/api/admin/backups')
      return response.data
    } catch (error) {
      throw error
    }
  },

  createBackup: async () => {
    try {
      const response = await api.post('/api/admin/backups')
      toast.success('پشتیبان با موفقیت ایجاد شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Knowledge base
  getKnowledgeBases: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/knowledge', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getKnowledgeBase: async (kbId: number) => {
    try {
      const response = await api.get(`/api/admin/knowledge/${kbId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateKnowledgeBase: async (kbId: number, data: any) => {
    try {
      const response = await api.put(`/api/admin/knowledge/${kbId}`, data)
      toast.success('پایگاه دانش با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  createKnowledge: async (data: any) => {
    try {
      const response = await api.post('/api/admin/knowledge', data)
      toast.success('دانش جدید با موفقیت ایجاد شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Fallback management
  getFallbacks: async (params?: any) => {
    try {
      const response = await api.get('/api/admin/fallbacks', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },

  getFallback: async (fallbackId: number) => {
    try {
      const response = await api.get(`/api/admin/fallbacks/${fallbackId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateFallback: async (fallbackId: number, data: any) => {
    try {
      const response = await api.put(`/api/admin/fallbacks/${fallbackId}`, data)
      toast.success('فال‌بک با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Ticket management
  createTicket: async (data: any) => {
    try {
      const response = await api.post('/api/tickets', data)
      toast.success('تیکت با موفقیت ایجاد شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Discount management
  getDiscounts: async () => {
    try {
      const response = await api.get('/api/admin/discounts')
      return response.data
    } catch (error) {
      throw error
    }
  },

  getDiscount: async (id: string) => {
    try {
      const response = await api.get(`/api/admin/discounts/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  createDiscount: async (data: any) => {
    try {
      const response = await api.post('/api/admin/discounts', data)
      toast.success('کد تخفیف با موفقیت ایجاد شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  updateDiscount: async (discountId: number, data: any) => {
    try {
      const response = await api.put(`/api/admin/discounts/${discountId}`, data)
      toast.success('کد تخفیف با موفقیت بروزرسانی شد')
      return response.data
    } catch (error) {
      throw error
    }
  },

  getDiscountRedemptions: async (discountId: number) => {
    try {
      const response = await api.get(`/api/admin/discounts/${discountId}/redemptions`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default api 