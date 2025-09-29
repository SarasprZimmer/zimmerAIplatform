'use client'

import { useState, useRef, useEffect } from 'react'
import { BellIcon, UserIcon, Cog6ToothIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import NotificationsBell from '@/components/notifications/NotificationsBell'
import { ThemeToggleCompact } from './ThemeToggle'

export default function Topbar() {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleProfileClick = () => {
    setIsProfileDropdownOpen(!isProfileDropdownOpen)
  }

  const handleSettingsClick = () => {
    router.push('/settings')
  }

  const handleViewProfile = () => {
    router.push('/settings')
    setIsProfileDropdownOpen(false)
  }

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 font-farhang transition-colors duration-200">
      <div className="flex items-center justify-between">
        {/* Left side - Logo and Dashboard text */}
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm sm:text-lg">Z</span>
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-purple-600 dark:text-purple-400">Zimmer</h1>
          </div>
          <div className="hidden sm:block h-6 w-px bg-gray-200 dark:bg-gray-600"></div>
          <h2 className="hidden sm:block text-lg font-semibold text-purple-600 dark:text-purple-400">داشبورد</h2>
        </div>

        {/* Right side - User icons */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Theme Toggle - Always Visible */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">تم:</span>
            <ThemeToggleCompact />
          </div>

          {/* User Profile Icon with Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button 
              onClick={handleProfileClick}
              className="relative p-2 sm:p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl transition-all duration-300 flex items-center gap-1"
            >
              <UserIcon className="w-5 h-5 sm:w-6 sm:h-6" />
              <ChevronDownIcon className="w-3 h-3 sm:w-4 sm:h-4" />
            </button>

            {/* Profile Dropdown Menu */}
            {isProfileDropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50 transform -translate-x-48">
                {/* User Info Section */}
                <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-700 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-sm">
                        {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {user?.name || 'کاربر'}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {user?.email}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="py-1">
                  <button
                    onClick={handleViewProfile}
                    className="w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 text-right flex items-center gap-3"
                  >
                    <UserIcon className="w-4 h-4" />
                    مشاهده پروفایل
                  </button>
                  
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 text-right flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    خروج از حساب
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Notifications */}
          <NotificationsBell />

          {/* Settings */}
          <button 
            onClick={handleSettingsClick}
            className="relative p-2 sm:p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl transition-all duration-300"
            title="تنظیمات"
          >
            <Cog6ToothIcon className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
        </div>
      </div>
    </div>
  )
} 