'use client'

import Link from 'next/link'
import { useRouter } from 'next/router'
import { 
  HomeIcon, 
  CogIcon, 
  CreditCardIcon, 
  UserIcon,
  RocketLaunchIcon,
  ArrowRightOnRectangleIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '@/contexts/AuthContext'

const navigationItems = [
  {
    name: 'داشبورد',
    href: '/dashboard',
    icon: HomeIcon,
    description: 'نمای کلی و آمار'
  },
  {
    name: 'اتوماسیون ها',
    href: '/automations',
    icon: RocketLaunchIcon,
    description: 'مدیریت گردش‌های هوشمند'
  },
  {
    name: 'مدیریت پرداخت ها',
    href: '/payment',
    icon: CreditCardIcon,
    description: 'صورتحساب و اشتراک‌ها'
  },
  {
    name: 'پشتیبانی',
    href: '/support',
    icon: QuestionMarkCircleIcon,
    description: 'تیکت‌ها و سوالات متداول'
  },
  {
    name: 'تنظیمات',
    href: '/settings',
    icon: CogIcon,
    description: 'تنظیمات حساب کاربری'
  }
]

export default function Sidebar() {
  const router = useRouter()
  const { logout } = useAuth()

  const getActiveState = (href: string) => {
    return router.pathname === href ? 'active' : ''
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="hidden lg:flex w-72 bg-white dark:bg-gray-800 shadow-lg h-screen fixed right-0 top-0 z-50 border-l border-gray-100 dark:border-gray-700 flex-col font-farhang transition-colors duration-200">
      {/* Logo Section - Fixed */}
      <div className="p-8 border-b border-gray-100 dark:border-gray-700 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">Z</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Zimmer AI</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">اتوماسیون هوشمند</p>
              </div>
            </div>
          </div>
      </div>

      {/* User Profile Section - Fixed */}
      <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex-shrink-0">
        <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
          <div className="w-10 h-10 bg-gradient-to-br from-gray-400 to-gray-600 rounded-xl flex items-center justify-center">
            <UserIcon className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">خوش آمدید</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">عضو ویژه</p>
          </div>
        </div>
      </div>

      {/* Navigation - Scrollable */}
      <nav className="flex-1 p-6 space-y-2 overflow-y-auto sidebar-scrollable">
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3 px-3">
            منوی اصلی
          </h3>
          <div className="space-y-1">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`sidebar-item ${getActiveState(item.href)} group`}
              >
                <div className="flex items-center gap-3 flex-1">
                  <item.icon className="w-5 h-5" />
                  <div className="flex-1 min-w-0">
                    <span className="font-medium">{item.name}</span>
                    <p className="text-xs text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400 transition-colors">
                      {item.description}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Logout Section - Fixed at Bottom */}
      <div className="p-6 border-t border-gray-100 dark:border-gray-700 flex-shrink-0">
        <button 
          onClick={handleLogout}
          className="sidebar-item w-full text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-300 group"
        >
          <ArrowRightOnRectangleIcon className="w-5 h-5" />
          <div className="flex-1 text-right">
            <span className="font-medium">خروج</span>
            <p className="text-xs text-red-400 dark:text-red-500 group-hover:text-red-500 dark:group-hover:text-red-400 transition-colors">
              خروج از حساب کاربری
            </p>
          </div>
        </button>
      </div>
    </div>
  )
} 