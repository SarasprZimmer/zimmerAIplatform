"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { fetchCsrf } from "@/lib/csrf";

type Status = { enabled: boolean };

export default function SecurityPage() {
  const [status, setStatus] = useState<Status>({enabled:false});
  const [otpauth, setOtpauth] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [backup, setBackup] = useState<string[] | null>(null);
  const [busy, setBusy] = useState(false);

  async function loadStatus() {
    const r = await apiFetch("/api/auth/2fa/status");
    if (r.ok) setStatus(await r.json());
  }

  useEffect(() => {
    fetchCsrf(process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || "https://193.162.129.243:8000");
    loadStatus();
  }, []);

  async function initiate() {
    setBusy(true);
    const r = await apiFetch("/api/auth/2fa/initiate", { method:"POST" });
    setBusy(false);
    if (!r.ok) return;
    const j = await r.json();
    setOtpauth(j.otpauth_uri);
  }

  async function activate() {
    setBusy(true);
    const r = await apiFetch("/api/auth/2fa/activate", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ otp_code: code })
    });
    setBusy(false);
    if (!r.ok) return;
    const j = await r.json();
    setBackup(j.recovery_codes || null);
    setOtpauth(null);
    setCode("");
    await loadStatus();
  }

  async function disable2fa() {
    setBusy(true);
    await apiFetch("/api/auth/2fa/disable", { method:"POST" });
    setBusy(false);
    setBackup(null);
    setOtpauth(null);
    setCode("");
    await loadStatus();
  }

  async function regen() {
    const r = await apiFetch("/api/auth/2fa/recovery-codes/regenerate", { method:"POST" });
    if (r.ok) {
      const j = await r.json();
      setBackup(j.codes);
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 text-right">
      <h1 className="text-xl font-semibold mb-4">امنیت حساب</h1>

      <div className="rounded-2xl border p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">تأیید دومرحله‌ای (2FA)</div>
            <div className="text-sm opacity-70">{status.enabled ? "فعال" : "غیرفعال"}</div>
          </div>
          {!status.enabled ? (
            <button onClick={initiate} disabled={busy} className="px-4 py-2 rounded-xl bg-black text-white">فعال‌سازی</button>
          ) : (
            <button onClick={disable2fa} disabled={busy} className="px-4 py-2 rounded-xl border">غیرفعال‌سازی</button>
          )}
        </div>

        {!status.enabled && otpauth && (
          <div className="mt-4 space-y-3">
            <div className="text-sm">کد QR زیر را با برنامه‌های Google Authenticator, 1Password یا Authy اسکن کنید.</div>
            <QRCode uri={otpauth} />
            <div className="flex gap-2 items-center">
              <input className="border rounded-xl p-3 flex-1" placeholder="کد ۶ رقمی" value={code} onChange={e=>setCode(e.target.value)} dir="ltr" />
              <button onClick={activate} disabled={busy || code.length<6} className="px-4 py-2 rounded-xl bg-black text-white">تأیید و فعال‌سازی</button>
            </div>
          </div>
        )}

        {backup && (
          <div className="mt-4">
            <div className="font-medium mb-2">کدهای پشتیبان (فقط همین یک‌بار نمایش داده می‌شود)</div>
            <ul className="grid grid-cols-2 gap-2 text-sm font-mono">
              {backup.map((c)=> <li key={c} className="border rounded-xl p-2" dir="ltr">{c}</li>)}
            </ul>
            <button onClick={regen} className="mt-3 px-3 py-2 rounded-xl border">تولید مجدد کدها</button>
          </div>
        )}
      </div>
    </div>
  );
}

function QRCode({ uri }: { uri: string }) {
  // lightweight QR using Google Chart API (no deps). Replace with a local lib if you prefer.
  const url = `https://chart.googleapis.com/chart?cht=qr&chs=220x220&chl=${encodeURIComponent(uri)}`;
  return <img src={url} alt="QR" className="w-[220px] h-[220px] rounded-xl border" />;
}
