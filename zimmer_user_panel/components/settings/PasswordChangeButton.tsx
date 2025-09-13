"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import PasswordChangeModal from "./PasswordChangeModal";

type Me = { 
  email?: string; 
  email_verified_at?: string | null;
};

export default function PasswordChangeButton() {
  const { api } = useAuth();
  const [me, setMe] = useState<Me | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const userData = await api.getCurrentUser();
        setMe(userData);
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      }
    })();
  }, [api]);

  const emailVerified = !!me?.email_verified_at;

  return (
    <>
      <div className="max-w-2xl space-y-4" dir="rtl">
        <div className="text-lg font-semibold">تغییر رمز عبور</div>
        
        <div className="p-4 border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">رمز عبور</div>
              <div className="text-xs text-gray-500">
                {emailVerified 
                  ? "برای تغییر رمز عبور روی دکمه زیر کلیک کنید" 
                  : "ابتدا باید ایمیل خود را تأیید کنید"}
              </div>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              disabled={!emailVerified}
              className={`px-4 py-2 rounded-xl font-medium transition-colors ${
                emailVerified
                  ? "bg-purple-600 text-white hover:bg-purple-700"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              تغییر رمز عبور
            </button>
          </div>
          
          {!emailVerified && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-sm text-yellow-800">
                <strong>توجه:</strong> برای تغییر رمز عبور، ابتدا باید ایمیل خود را در بخش &quot;امنیت حساب&quot; تأیید کنید.
              </div>
            </div>
          )}
        </div>
      </div>

      <PasswordChangeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        userEmail={me?.email}
        isEmailVerified={emailVerified}
      />
    </>
  );
}
