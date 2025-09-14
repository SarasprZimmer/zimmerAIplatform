const BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"

class ApiClient {
  // Simple authentication methods without CSRF complexity
  async login(email: string, password: string) {
    console.log(" API: Login attempt for:", email)
    
    try {
      const response = await fetch(`${BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password }),
        credentials: "include"
      })

      console.log(" API: Login response status:", response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.log(" API: Login error response:", errorText)
        
        // Handle 2FA challenge
        if (response.status === 401) {
          try {
            const errorData = JSON.parse(errorText)
            if (errorData.error === "otp_required" && errorData.challenge_token) {
              throw { status: 401, data: errorData }
            }
          } catch (e) {
            // If parsing fails, continue with normal error handling
          }
        }
        
        let errorMessage = "Login failed"
        try {
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
          // Provide user-friendly messages based on status
          if (response.status === 401) {
            errorMessage = "ایمیل یا رمز عبور اشتباه است"
          } else if (response.status === 404) {
            errorMessage = "کاربری با این ایمیل یافت نشد"
          } else if (response.status >= 500) {
            errorMessage = "خطا در سرور. لطفا دوباره تلاش کنید"
          } else {
            errorMessage = "خطا در ورود. لطفا دوباره تلاش کنید"
          }
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      console.log(" API: Login successful")
      
      // Store the token in localStorage for now
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
      }
      
      return data
    } catch (error) {
      console.error(" API: Login error:", error)
      throw error
    }
  }

  async signup(email: string, password: string, name: string) {
    console.log(" API: Signup attempt for:", email)
    
    try {
      const response = await fetch(`${BASE_URL}/api/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password, name }),
        credentials: "include"
      })

      console.log(" API: Signup response status:", response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.log(" API: Signup error response:", errorText)
        
        let errorMessage = "Signup failed"
        try {
          const errorData = JSON.parse(errorText)
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
          // Provide user-friendly messages based on status
          if (response.status === 400) {
            errorMessage = "اطلاعات وارد شده صحیح نیست"
          } else if (response.status === 409) {
            errorMessage = "کاربری با این ایمیل قبلا وجود دارد"
          } else if (response.status >= 500) {
            errorMessage = "خطا در سرور. لطفا دوباره تلاش کنید"
          } else {
            errorMessage = "خطا در ثبت نام. لطفا دوباره تلاش کنید"
          }
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      console.log(" API: Signup successful")
      
      // Store the token in localStorage for now
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
      }
      
      return data
    } catch (error) {
      console.error(" API: Signup error:", error)
      throw error
    }
  }

  async logout() {
    try {
      await fetch(`${BASE_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include"
      })
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      localStorage.removeItem("access_token")
    }
  }

  async verifyOtp(challenge_token: string, otp_code: string) {
    console.log(" API: OTP verification attempt")
    
    try {
      const response = await fetch(`${BASE_URL}/api/auth/2fa/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ challenge_token, otp_code }),
        credentials: "include"
      })

      console.log(" API: OTP verification response status:", response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.log(" API: OTP verification error response:", errorText)
        throw new Error("OTP verification failed")
      }

      const data = await response.json()
      console.log(" API: OTP verification successful")
      
      // Store the token in localStorage
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
      }
      
      return data
    } catch (error) {
      console.error(" API: OTP verification error:", error)
      throw error
    }
  }

  async refreshToken() {
    try {
      const response = await fetch(`${BASE_URL}/api/auth/refresh`, {
        method: "POST",
        credentials: "include"
      })

      if (!response.ok) {
        throw new Error("Token refresh failed")
      }

      const data = await response.json()
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token)
      }
      return data
    } catch (error) {
      console.error("Refresh token error:", error)
      throw error
    }
  }

  async getCurrentUser() {
    const token = localStorage.getItem("access_token")
    if (!token) {
      throw new Error("No access token")
    }

    const response = await fetch(`${BASE_URL}/api/me`, {
      headers: {
        "Authorization": `Bearer ${token}`
      },
      credentials: "include"
    })

    if (!response.ok) {
      throw new Error("Failed to get user info")
    }

    return response.json()
  }

  async forgotPassword(email: string) {
    const response = await fetch(`${BASE_URL}/api/forgot-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email }),
      credentials: "include"
    })

    if (!response.ok) {
      throw new Error("Failed to send password reset email")
    }

    return response.json()
  }

  async resetPassword(token: string, newPassword: string) {
    const response = await fetch(`${BASE_URL}/api/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ token, new_password: newPassword }),
      credentials: "include"
    })

    if (!response.ok) {
      throw new Error("Failed to reset password")
    }

    return response.json()
  }

  // Simple token management
  getAccessToken() {
    return localStorage.getItem("access_token")
  }

  isAuthenticated() {
    return !!localStorage.getItem("access_token")
  }

  clearAccessToken() {
    localStorage.removeItem("access_token")
  }
}

export default ApiClient
