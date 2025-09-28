"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function TestGoogleAuth() {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkGoogleConfig = async () => {
      try {
        const api = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com";
        const response = await fetch(`${api}/api/auth/google/configured`);
        
        if (response.ok) {
          const data = await response.json();
          setConfig(data);
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    checkGoogleConfig();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p>در حال بررسی تنظیمات...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-2xl font-bold mb-6">تست احراز هویت گوگل</h1>
          
          {error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <h3 className="text-red-800 font-semibold mb-2">خطا</h3>
              <p className="text-red-700">{error}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-blue-800 font-semibold mb-2">وضعیت تنظیمات گوگل</h3>
                <p className="text-blue-700">
                  {config?.configured ? "✅ پیکربندی شده" : "❌ پیکربندی نشده"}
                </p>
              </div>
              
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h3 className="text-gray-800 font-semibold mb-2">جزئیات پاسخ</h3>
                <pre className="text-sm text-gray-700 overflow-auto">
                  {JSON.stringify(config, null, 2)}
                </pre>
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-yellow-800 font-semibold mb-2">تست لینک ورود</h3>
                <p className="text-yellow-700 mb-2">
                  برای تست کامل، روی لینک زیر کلیک کنید:
                </p>
                <a 
                  href="/api/auth/google/login"
                  className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                >
                  ورود با گوگل
                </a>
              </div>
            </div>
          )}
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <Link 
              href="/login"
              className="text-purple-600 hover:text-purple-700 font-medium"
            >
              ← بازگشت به صفحه ورود
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
