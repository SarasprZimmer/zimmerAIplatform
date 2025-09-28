'use client'

import React, { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/router'
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface DeleteAccountModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function DeleteAccountModal({ isOpen, onClose }: DeleteAccountModalProps) {
  const { logout } = useAuth()
  const router = useRouter()
  const [isDeleting, setIsDeleting] = useState(false)
  const [confirmationText, setConfirmationText] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleDeleteAccount = async () => {
    if (confirmationText !== 'حذف حساب') {
      setError('لطفاً متن تأیید را دقیقاً وارد کنید')
      return
    }

    setIsDeleting(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        throw new Error('توکن دسترسی یافت نشد')
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/auth/delete-account`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'خطا در حذف حساب کاربری')
      }

      // Clear local storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      // Redirect to home page
      router.push('/')
      
      // Show success message
      alert('حساب کاربری شما با موفقیت حذف شد')

    } catch (err: any) {
      setError(err.message || 'خطا در حذف حساب کاربری')
    } finally {
      setIsDeleting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              حذف حساب کاربری
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Warning Content */}
        <div className="mb-6">
          <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-red-800 dark:text-red-300 mb-2">
              ⚠️ هشدار: این عمل غیرقابل بازگشت است
            </h3>
            <ul className="text-sm text-red-700 dark:text-red-400 space-y-1">
              <li>• تمام اطلاعات شخصی شما حذف خواهد شد</li>
              <li>• تمام اتوماسیون‌ها و تنظیمات شما از بین خواهد رفت</li>
              <li>• تاریخچه پرداخت‌ها و استفاده حذف خواهد شد</li>
              <li>• این عمل قابل بازگشت نیست</li>
            </ul>
          </div>

          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
            برای تأیید حذف حساب کاربری، لطفاً عبارت <strong className="text-red-600 dark:text-red-400">&quot;حذف حساب&quot;</strong> را در کادر زیر وارد کنید:
          </p>

          <input
            type="text"
            value={confirmationText}
            onChange={(e) => setConfirmationText(e.target.value)}
            placeholder="حذف حساب"
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            dir="rtl"
          />

          {error && (
            <p className="text-red-600 dark:text-red-400 text-sm mt-2">{error}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            disabled={isDeleting}
          >
            انصراف
          </button>
          <button
            onClick={handleDeleteAccount}
            disabled={isDeleting || confirmationText !== 'حذف حساب'}
            className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {isDeleting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                در حال حذف...
              </>
            ) : (
              'حذف حساب کاربری'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
