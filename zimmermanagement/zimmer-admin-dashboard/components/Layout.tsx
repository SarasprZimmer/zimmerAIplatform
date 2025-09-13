import React from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import ProtectedRoute from './ProtectedRoute'
import MobileBottomNav from './MobileBottomNav'

interface LayoutProps {
  children: React.ReactNode
  title: string
}

const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <ProtectedRoute>
      <div className="rtl flex h-screen bg-gray-100">
        <div className="flex-1 flex flex-col overflow-hidden">
          <Topbar title={title} />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4 sm:p-6 pb-20 md:pb-6">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
        <Sidebar />
        <MobileBottomNav />
      </div>
    </ProtectedRoute>
  )
}

export default Layout 