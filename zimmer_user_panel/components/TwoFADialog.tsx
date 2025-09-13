"use client";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function TwoFADialog({
  challengeToken, onSuccess, onCancel
}: { challengeToken: string; onSuccess: () => void; onCancel: () => void; }) {
  const [code, setCode] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const { verifyOtp } = useAuth();

  async function submit() {
    setBusy(true); setErr(null);
    try {
      await verifyOtp(challengeToken, code.trim());
      onSuccess();
    } catch {
      setErr("کد وارد شده معتبر نیست.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 text-right">
        <h2 className="text-lg font-semibold mb-2">تأیید دومرحله‌ای</h2>
        <p className="text-sm opacity-80 mb-4">کد ۶ رقمی برنامه احراز هویت یا یکی از کدهای پشتیبان را وارد کنید.</p>
        <input
          inputMode="numeric"
          className="w-full border rounded-xl p-3 mb-3"
          placeholder="123456"
          value={code}
          onChange={(e)=>setCode(e.target.value)}
          dir="ltr"
        />
        {err && <div className="text-red-600 text-sm mb-2">{err}</div>}
        <div className="flex gap-2 justify-end">
          <button onClick={onCancel} className="px-4 py-2 rounded-xl border">انصراف</button>
          <button onClick={submit} disabled={busy || !code} className="px-4 py-2 rounded-xl bg-black text-white">
            {busy ? "در حال بررسی..." : "تأیید"}
          </button>
        </div>
      </div>
    </div>
  );
}
