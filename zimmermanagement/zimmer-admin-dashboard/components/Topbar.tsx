import React from 'react'
import { useAuth } from '../contexts/AuthContext'

interface TopbarProps {
  title: string
}

const Topbar: React.FC<TopbarProps> = ({ title }) => {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-4 sm:px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg sm:text-xl font-semibold text-gray-900 truncate">{title}</h1>
        
        <div className="flex items-center space-x-2 sm:space-x-4">
          <span className="hidden sm:block text-sm text-gray-600">
            خوش آمدید، {user?.name || 'کاربر'}
          </span>
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 text-white px-3 sm:px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200"
          >
            <span className="hidden sm:inline">خروج</span>
            <span className="sm:hidden">خروج</span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Topbar 