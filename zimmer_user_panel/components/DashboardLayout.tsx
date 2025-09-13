'use client'

import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

interface DashboardLayoutProps {
  children: ReactNode
  user?: any // Optional user prop for compatibility
}

export default function DashboardLayout({ children, user }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 font-farhang">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="lg:mr-72">
        {/* Topbar */}
        <Topbar />
        
        {/* Page Content */}
        <main className="min-h-screen">
          <div className="page-container">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
