"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function VerifyEmailPage() {
  const [state, setState] = useState<"idle"|"ok"|"error">("idle");
  const [msg, setMsg] = useState("در حال بررسی لینک تأیید...");

  useEffect(() => {
    const url = new URL(window.location.href);
    const token = url.searchParams.get("token");
    if (!token) { setState("error"); setMsg("توکن تأیید یافت نشد."); return; }
    (async () => {
      try {
        const res = await fetch((process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "https://193.162.129.243:8000") + "/api/auth/verify-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ token })
        });
        if (res.ok) { setState("ok"); setMsg("ایمیل شما با موفقیت تأیید شد."); }
        else {
          const j = await res.json().catch(()=>({detail:"خطا در تأیید"}));
          setState("error"); setMsg(j?.detail || "خطا در تأیید");
        }
      } catch { setState("error"); setMsg("عدم دسترسی به سرور"); }
    })();
  }, []);

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-8">
      <div className="max-w-md w-full rounded-2xl shadow p-6 text-center">
        <h1 className="text-xl mb-2">تأیید ایمیل</h1>
        <p className="opacity-80">{msg}</p>
        {state==="ok" && <Link href="/login" className="inline-block mt-4 underline">رفتن به صفحه ورود</Link>}
      </div>
    </div>
  );
}
