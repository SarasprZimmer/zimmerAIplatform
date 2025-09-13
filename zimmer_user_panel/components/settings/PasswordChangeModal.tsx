"use client";
import { useState } from "react";

interface PasswordChangeModalProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail?: string;
  isEmailVerified?: boolean;
}

export default function PasswordChangeModal({ 
  isOpen, 
  onClose, 
  userEmail, 
  isEmailVerified = false 
}: PasswordChangeModalProps) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [useEmailVerification, setUseEmailVerification] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const resetForm = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setVerificationCode("");
    setUseEmailVerification(false);
    setCodeSent(false);
    setMsg(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const sendVerificationCode = async () => {
    if (!userEmail) return;
    
    setBusy(true);
    setMsg(null);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/auth/send-password-reset-code`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ email: userEmail })
      });
      
      if (response.ok) {
        setCodeSent(true);
        setMsg("کد تأیید به ایمیل شما ارسال شد.");
      } else {
        setMsg("خطا در ارسال کد تأیید.");
      }
    } catch (error) {
      setMsg("خطا در ارسال کد تأیید.");
    } finally {
      setBusy(false);
    }
  };

  const submitPasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newPassword || !confirmPassword) {
      setMsg("رمز عبور جدید و تکرار آن را وارد کنید.");
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setMsg("رمزهای عبور یکسان نیستند.");
      return;
    }
    
    if (newPassword.length < 6) {
      setMsg("رمز عبور باید حداقل ۶ کاراکتر باشد.");
      return;
    }

    setBusy(true);
    setMsg(null);
    
    try {
      let requestBody;
      
      if (useEmailVerification) {
        if (!verificationCode) {
          setMsg("کد تأیید را وارد کنید.");
          setBusy(false);
          return;
        }
        requestBody = {
          new_password: newPassword,
          confirm_password: confirmPassword,
          verification_code: verificationCode
        };
      } else {
        if (!currentPassword) {
          setMsg("رمز عبور فعلی را وارد کنید.");
          setBusy(false);
          return;
        }
        requestBody = {
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        };
      }
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.zimmerai.com"}/api/user/password`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify(requestBody)
      });
      
      if (response.ok) {
        setMsg("رمز عبور با موفقیت تغییر کرد.");
        setTimeout(() => {
          handleClose();
        }, 2000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setMsg(errorData.detail || "خطا در تغییر رمز عبور.");
      }
    } catch (error) {
      setMsg("خطا در تغییر رمز عبور.");
    } finally {
      setBusy(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6" dir="rtl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">تغییر رمز عبور</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={submitPasswordChange} className="space-y-4">
          {/* Method Selection */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              روش تأیید هویت:
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="verification_method"
                  checked={!useEmailVerification}
                  onChange={() => setUseEmailVerification(false)}
                  className="mr-2"
                />
                <span className="text-sm">رمز عبور فعلی</span>
              </label>
              {isEmailVerified && (
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="verification_method"
                    checked={useEmailVerification}
                    onChange={() => setUseEmailVerification(true)}
                    className="mr-2"
                  />
                  <span className="text-sm">کد تأیید از ایمیل</span>
                </label>
              )}
            </div>
          </div>

          {/* Current Password or Email Verification */}
          {!useEmailVerification ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                رمز عبور فعلی
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="رمز عبور فعلی خود را وارد کنید"
                required
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                کد تأیید
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="کد تأیید"
                  required
                />
                <button
                  type="button"
                  onClick={sendVerificationCode}
                  disabled={busy || codeSent}
                  className="px-4 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {codeSent ? "ارسال شد" : "ارسال کد"}
                </button>
              </div>
            </div>
          )}

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              رمز عبور جدید
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="رمز عبور جدید"
              required
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              تکرار رمز عبور جدید
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="تکرار رمز عبور جدید"
              required
            />
          </div>

          {/* Message */}
          {msg && (
            <div className={`p-3 rounded-xl text-sm ${
              msg.includes("موفقیت") 
                ? "bg-green-50 text-green-800 border border-green-200" 
                : "bg-red-50 text-red-800 border border-red-200"
            }`}>
              {msg}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={busy}
              className="flex-1 px-4 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {busy ? "در حال تغییر..." : "تغییر رمز عبور"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
