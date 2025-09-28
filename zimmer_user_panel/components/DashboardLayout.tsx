'use client'

import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import MobileBottomNav from './MobileBottomNav'

interface DashboardLayoutProps {
  children: ReactNode
  user?: any // Optional user prop for compatibility
}

export default function DashboardLayout({ children, user }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 font-farhang transition-colors duration-200">
      {/* Sidebar - Hidden on mobile, shown on desktop */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="lg:mr-72">
        {/* Topbar */}
        <Topbar />
        
        {/* Page Content */}
        <main className="min-h-screen pb-16 lg:pb-0 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
          <div className="page-container">
            {children}
          </div>
        </main>
      </div>
      
      {/* Mobile Bottom Navigation */}
      <MobileBottomNav />
    </div>
  )
}
