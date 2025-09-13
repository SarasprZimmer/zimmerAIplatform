"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { rial } from "@/lib/money";

type ValidateOut = {
  valid: boolean;
  code?: string;
  percent_off?: number;
  amount_before?: number;
  amount_discount?: number;
  amount_after?: number;
  reason?: string;
};

export default function DiscountCodeField({
  automationId,
  baseAmount,
  onApplied,
  onCleared,
}: {
  automationId: number;
  baseAmount: number;
  onApplied: (res: ValidateOut) => void;
  onCleared: () => void;
}) {
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [applied, setApplied] = useState<ValidateOut | null>(null);

  async function apply() {
    setBusy(true); setMsg(null);
    try {
      const res = await apiFetch("/api/discounts/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, automation_id: automationId, amount: baseAmount }),
      });
      const j: ValidateOut = await res.json();
      if (!j.valid) {
        setApplied(null);
        setMsg(reasonToFa(j.reason || "invalid"));
        onCleared();
        return;
      }
      setApplied(j);
      onApplied(j);
      setMsg(`کد اعمال شد: ${j.code} (${j.percent_off}% - ${rial(j.amount_discount || 0)} ریال)`);
    } catch {
      setMsg("خطا در بررسی کد تخفیف.");
    } finally {
      setBusy(false);
    }
  }

  function clearCode() {
    setApplied(null);
    setCode("");
    setMsg(null);
    onCleared();
  }

  return (
    <div className="border rounded-2xl p-4 space-y-2">
      <div className="font-medium">کد تخفیف</div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-xl p-3"
          placeholder="مثلاً WELCOME20"
          value={code}
          onChange={(e)=>setCode(e.target.value.toUpperCase())}
          dir="ltr"
        />
        {!applied ? (
          <button onClick={apply} disabled={busy || !code.trim()} className="px-4 py-2 rounded-xl bg-black text-white">
            {busy ? "در حال بررسی..." : "اعمال"}
          </button>
        ) : (
          <button onClick={clearCode} className="px-4 py-2 rounded-xl border">حذف</button>
        )}
      </div>
      {applied && (
        <div className="text-sm text-green-700">
          اعمال شد: {applied.code} − {applied.percent_off}% (− {rial(applied.amount_discount || 0)} ریال)
        </div>
      )}
      {msg && <div className="text-sm opacity-75">{msg}</div>}
    </div>
  );
}

function reasonToFa(r: string) {
  switch (r) {
    case "not_found": return "کد یافت نشد.";
    case "inactive_or_window": return "این کد در حال حاضر فعال نیست.";
    case "not_applicable": return "این کد برای این اتوماسیون معتبر نیست.";
    case "max_redeemed": return "سقف استفاده از این کد پر شده است.";
    case "per_user_limit": return "سقف استفاده شما از این کد پر شده است.";
    default: return "کد معتبر نیست.";
  }
}
