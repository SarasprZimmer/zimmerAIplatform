"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Badge } from "@/components/ui/Kit";

type Me = { 
  email?: string; 
  email_verified_at?: string | null;
  name?: string;
};

export default function SecurityStatus(){
  const { api } = useAuth();
  const [me, setMe] = useState<Me | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [showCodeInput, setShowCodeInput] = useState(false);

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

  async function sendVerificationEmail() {
    if (!me?.email) return;
    setBusy(true); 
    setNote(null);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}/api/auth/send-email-verification`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ email: me.email })
      });
      
      if (response.ok) {
        setNote("کد تأیید به ایمیل شما ارسال شد. لطفاً کد را وارد کنید.");
        setShowCodeInput(true);
      } else {
        setNote("خطا در ارسال کد تأیید. لطفاً دوباره تلاش کنید.");
      }
    } catch (error) {
      setNote("خطا در ارسال کد تأیید. لطفاً دوباره تلاش کنید.");
    } finally { 
      setBusy(false); 
    }
  }

  async function verifyEmailCode() {
    if (!verificationCode.trim()) {
      setNote("لطفاً کد تأیید را وارد کنید.");
      return;
    }
    
    setBusy(true);
    setNote(null);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}/api/auth/verify-email`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ 
          email: me?.email,
          verification_code: verificationCode 
        })
      });
      
      if (response.ok) {
        setNote("ایمیل شما با موفقیت تأیید شد!");
        setShowCodeInput(false);
        setVerificationCode("");
        // Refresh user data
        try {
          const userData = await api.getCurrentUser();
          setMe(userData);
        } catch (error) {
          console.error("Failed to refresh user data:", error);
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        setNote(errorData.detail || "کد تأیید نامعتبر است. لطفاً دوباره تلاش کنید.");
      }
    } catch (error) {
      setNote("خطا در تأیید کد. لطفاً دوباره تلاش کنید.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-4" dir="rtl">
      <div className="text-lg font-semibold">امنیت حساب</div>
      
      <div className="space-y-4">
        {/* Email Verification */}
        <div className="p-4 border border-gray-200 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-sm font-medium text-gray-900">تأیید ایمیل</div>
              <div className="text-xs text-gray-500">{me?.email}</div>
            </div>
            <div className="flex items-center gap-2">
              {emailVerified ? (
                <Badge className="bg-emerald-100 text-emerald-800">تأیید شده</Badge>
              ) : (
                <Badge className="bg-yellow-100 text-yellow-800">تأیید نشده</Badge>
              )}
            </div>
          </div>
          
          {!emailVerified && (
            <div className="space-y-3">
              {!showCodeInput ? (
                <button 
                  onClick={sendVerificationEmail} 
                  disabled={busy} 
                  className="px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {busy ? "در حال ارسال..." : "ارسال کد تأیید"}
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      className="flex-1 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="کد تأیید ۶ رقمی"
                      maxLength={6}
                    />
                    <button
                      onClick={verifyEmailCode}
                      disabled={busy || !verificationCode.trim()}
                      className="px-4 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      تأیید
                    </button>
                  </div>
                  <button
                    onClick={() => {
                      setShowCodeInput(false);
                      setVerificationCode("");
                      setNote(null);
                    }}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    ارسال مجدد کد
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Security Notice */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="text-sm text-blue-800">
            <strong>نکته امنیتی:</strong> برای تغییر رمز عبور، ابتدا باید ایمیل خود را تأیید کنید.
          </div>
        </div>
      </div>
      
      {note && (
        <div className={`p-3 rounded-xl text-sm ${
          note.includes("موفقیت") || note.includes("تأیید شد") 
            ? "bg-green-50 text-green-800 border border-green-200" 
            : "bg-yellow-50 text-yellow-800 border border-yellow-200"
        }`}>
          {note}
        </div>
      )}
    </div>
  );
}

