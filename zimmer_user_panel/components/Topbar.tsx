'use client'

import { BellIcon, MagnifyingGlassIcon, UserIcon, Cog6ToothIcon } from '@heroicons/react/24/outline'
import NotificationsBell from '@/components/notifications/NotificationsBell'

export default function Topbar() {
  return (
    <div className="bg-white border-b border-gray-100 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 font-farhang">
      <div className="flex items-center justify-between">
        {/* Left side - Logo and Dashboard text */}
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm sm:text-lg">Z</span>
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-purple-600">Zimmer</h1>
          </div>
          <div className="hidden sm:block h-6 w-px bg-gray-200"></div>
          <h2 className="hidden sm:block text-lg font-semibold text-purple-600">داشبورد</h2>
        </div>

        {/* Center - Search bar (hidden on mobile) */}
        <div className="hidden md:flex flex-1 max-w-md mx-4 lg:mx-8">
          <div className="relative w-full">
            <MagnifyingGlassIcon className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="جستجو کردن"
              className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
            />
          </div>
        </div>

        {/* Right side - User icons */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Mobile search button */}
          <button className="md:hidden relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-300">
            <MagnifyingGlassIcon className="w-5 h-5" />
          </button>

          {/* User Profile Icon */}
          <button className="relative p-2 sm:p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-300">
            <UserIcon className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>

          {/* Notifications */}
          <NotificationsBell />

          {/* Settings */}
          <button className="relative p-2 sm:p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-300">
            <Cog6ToothIcon className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
        </div>
      </div>
    </div>
  )
} 