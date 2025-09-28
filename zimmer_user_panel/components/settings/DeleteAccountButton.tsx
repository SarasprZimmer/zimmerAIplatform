'use client'

import React, { useState } from 'react'
import { TrashIcon } from '@heroicons/react/24/outline'
import DeleteAccountModal from './DeleteAccountModal'

export default function DeleteAccountButton() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              حذف حساب کاربری
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              حذف دائمی حساب کاربری و تمام اطلاعات مرتبط
            </p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <TrashIcon className="w-5 h-5" />
            حذف حساب کاربری
          </button>
        </div>
      </div>

      <DeleteAccountModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  )
}
