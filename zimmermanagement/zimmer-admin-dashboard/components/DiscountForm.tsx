"use client";
import { useEffect, useMemo, useState } from "react";
import { adminAPI } from "@/lib/api";

type Automation = { id: number; name: string };
export type DiscountPayload = {
  code: string;
  percent_off: number;
  active: boolean;
  starts_at?: string | null;
  ends_at?: string | null;
  max_redemptions?: number | null;
  per_user_limit?: number | null;
  automation_ids: number[];
};

export default function DiscountForm({
  initial, onSubmit, submitLabel="Save"
}: {
  initial?: Partial<DiscountPayload>;
  onSubmit: (data: DiscountPayload) => Promise<void>;
  submitLabel?: string;
}) {
  const [code, setCode] = useState(initial?.code ?? "");
  const [percent, setPercent] = useState<number>(initial?.percent_off ?? 0);
  const [active, setActive] = useState<boolean>(initial?.active ?? true);
  const [startsAt, setStartsAt] = useState<string>(initial?.starts_at ?? "");
  const [endsAt, setEndsAt] = useState<string>(initial?.ends_at ?? "");
  const [maxRed, setMaxRed] = useState<string>(initial?.max_redemptions?.toString() ?? "");
  const [perUser, setPerUser] = useState<string>(initial?.per_user_limit?.toString() ?? "");
  const [selected, setSelected] = useState<number[]>(initial?.automation_ids ?? []);
  const [autos, setAutos] = useState<Automation[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const response = await adminAPI.getAutomations();
        // Handle different response formats - API returns {total_count, automations}
        const list = Array.isArray(response) ? response : (response?.automations || response?.data || []);
        setAutos(Array.isArray(list) ? list : []);
      } catch (error) {
        console.error('Error fetching automations:', error);
        setAutos([]);
      }
    })();
  }, []);

  const payload: DiscountPayload = useMemo(() => ({
    code: code.trim().toUpperCase(),
    percent_off: Number(percent),
    active,
    starts_at: startsAt ? new Date(startsAt).toISOString() : null,
    ends_at: endsAt ? new Date(endsAt).toISOString() : null,
    max_redemptions: maxRed ? Number(maxRed) : null,
    per_user_limit: perUser ? Number(perUser) : null,
    automation_ids: selected,
  }), [code, percent, active, startsAt, endsAt, maxRed, perUser, selected]);

  function toggleAutomation(id: number) {
    setSelected((prev) => prev.includes(id) ? prev.filter(x=>x!==id) : [...prev, id]);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null); setBusy(true);
    try {
      if (!payload.code || payload.code.length < 2) throw new Error("کد تخفیف معتبر نیست.");
      if (payload.percent_off < 0 || payload.percent_off > 100) throw new Error("درصد تخفیف باید بین 0 تا 100 باشد.");
      await onSubmit(payload);
    } catch (e: any) {
      setErr(e?.message || "خطا در ذخیره‌سازی");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm mb-1">کد تخفیف</label>
          <input className="w-full border rounded-xl p-3" value={code} onChange={e=>setCode(e.target.value)} placeholder="WELCOME20" />
        </div>
        <div>
          <label className="block text-sm mb-1">درصد تخفیف (0-100)</label>
          <input type="number" className="w-full border rounded-xl p-3" value={percent} onChange={e=>setPercent(Number(e.target.value))} />
        </div>
        <div>
          <label className="block text-sm mb-1">شروع اعتبار (اختیاری)</label>
          <input type="datetime-local" className="w-full border rounded-xl p-3" value={startsAt} onChange={e=>setStartsAt(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm mb-1">پایان اعتبار (اختیاری)</label>
          <input type="datetime-local" className="w-full border rounded-xl p-3" value={endsAt} onChange={e=>setEndsAt(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm mb-1">حداکثر دفعات استفاده (کلی)</label>
          <input type="number" className="w-full border rounded-xl p-3" value={maxRed} onChange={e=>setMaxRed(e.target.value)} placeholder="مثلاً 100" />
        </div>
        <div>
          <label className="block text-sm mb-1">حداکثر برای هر کاربر</label>
          <input type="number" className="w-full border rounded-xl p-3" value={perUser} onChange={e=>setPerUser(e.target.value)} placeholder="مثلاً 1" />
        </div>
      </div>

      <div className="border rounded-2xl p-4">
        <div className="flex items-center justify-between">
          <div className="font-medium">وضعیت</div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={active} onChange={e=>setActive(e.target.checked)} />
            فعال
          </label>
        </div>
      </div>

      <div className="border rounded-2xl p-4">
        <div className="font-medium mb-2">اعمال روی اتوماسیون‌ها</div>
        <div className="text-sm opacity-70 mb-3">اگر هیچ موردی انتخاب نشود، کد برای همه اتوماسیون‌ها معتبر است.</div>
        <div className="grid md:grid-cols-2 gap-2">
          {Array.isArray(autos) && autos.map(a => (
            <label key={a.id} className="flex items-center gap-2 border rounded-xl p-2">
              <input type="checkbox" checked={selected.includes(a.id)} onChange={()=>toggleAutomation(a.id)} />
              <span>{a.name} (#{a.id})</span>
            </label>
          ))}
          {(!Array.isArray(autos) || !autos.length) && <div className="text-sm opacity-60">اتوماسیونی یافت نشد.</div>}
        </div>
      </div>

      {err && <div className="text-sm text-red-600">{err}</div>}
      <div className="flex gap-2">
        <button disabled={busy} className="px-4 py-2 rounded-xl bg-black text-white">{busy ? "در حال ذخیره..." : submitLabel}</button>
      </div>
    </form>
  );
}
