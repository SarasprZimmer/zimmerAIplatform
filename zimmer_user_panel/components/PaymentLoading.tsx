'use client'

export default function PaymentLoading() {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 text-center max-w-md mx-4">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">در حال انتقال به درگاه پرداخت</h3>
        <p className="text-gray-500 mb-4">لطفاً صبر کنید...</p>
        <div className="text-sm text-gray-400">
          <p>در حال اتصال به زرین‌پال</p>
          <p className="mt-1">پس از تکمیل پرداخت به این صفحه بازخواهید گشت</p>
        </div>
      </div>
    </div>
  )
}