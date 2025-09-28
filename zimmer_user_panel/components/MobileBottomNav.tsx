'use client'

import Link from 'next/link'
import { useRouter } from 'next/router'
import { 
  HomeIcon, 
  CogIcon, 
  CreditCardIcon, 
  UserIcon,
  RocketLaunchIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'

const navigationItems = [
  {
    name: 'داشبورد',
    href: '/dashboard',
    icon: HomeIcon,
  },
  {
    name: 'اتوماسیون ها',
    href: '/automations',
    icon: RocketLaunchIcon,
  },
  {
    name: 'پرداخت ها',
    href: '/payment',
    icon: CreditCardIcon,
  },
  {
    name: 'پشتیبانی',
    href: '/support',
    icon: QuestionMarkCircleIcon,
  },
  {
    name: 'تنظیمات',
    href: '/settings',
    icon: CogIcon,
  }
]

export default function MobileBottomNav() {
  const router = useRouter()

  const getActiveState = (href: string) => {
    if (href === '/dashboard') {
      return router.pathname === '/dashboard'
    }
    return router.pathname.startsWith(href)
  }

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50 transition-colors duration-200">
      <div className="flex justify-around items-center h-16 px-2">
        {navigationItems.map((item) => {
          const isActive = getActiveState(item.href)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`mobile-nav-item ${isActive ? 'active' : ''}`}
            >
              <div className="flex-shrink-0 mb-1">
                <item.icon className="w-5 h-5" />
              </div>
              <span className="text-xs font-medium text-center leading-tight">
                {item.name}
              </span>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
