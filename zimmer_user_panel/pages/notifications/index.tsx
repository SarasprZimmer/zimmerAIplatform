"use client";
import { useEffect, useMemo, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import DashboardLayout from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/apiClient";
import { Notify, routeForNotification, typeLabel } from "@/lib/notifications";

type Tab = "all" | "unread" | "payment" | "ticket" | "automation" | "admin";

const LIMIT = 20;

export default function NotificationsPage(){
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("all");
  const [items, setItems] = useState<Notify[]|null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [busy, setBusy] = useState(false);
  const [selectMode, setSelectMode] = useState(false);
  const [selected, setSelected] = useState<Record<number,boolean>>({});

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  const typeParam = useMemo(()=> tab==="all"||tab==="unread" ? "" : tab, [tab]);
  const readParam = useMemo(()=> tab==="unread" ? "false" : "", [tab]);

  const load = useCallback(async (reset:boolean) => {
    const params = new URLSearchParams();
    params.set("limit", String(LIMIT));
    params.set("offset", String(reset?0:offset));
    if(typeParam) params.set("type", typeParam);
    if(readParam) params.set("read", readParam);
    const r = await apiFetch(`/api/notifications?${params.toString()}`);
    if(!r.ok){ if(reset) setItems([]); return; }
    const j = await r.json();
    const batch: Notify[] = Array.isArray(j) ? j : (j.items||[]);
    if(reset){ setItems(batch); setOffset(batch.length); setHasMore(batch.length===LIMIT); }
    else { setItems(prev => [ ...(prev||[]), ...batch ]); setOffset(o=>o+batch.length); setHasMore(batch.length===LIMIT); }
  }, [offset, typeParam, readParam])

  useEffect(()=>{ if(isAuthenticated) load(true); },[tab, isAuthenticated, load]);

  function toggle(id:number){ setSelected(s => ({...s, [id]: !s[id]})); }
  function clearSelection(){ setSelected({}); }

  async function markSelected(){
    const ids = Object.entries(selected).filter(([,v])=>v).map(([k])=>Number(k));
    if(ids.length===0) return;
    setBusy(true);
    try{
      await apiFetch("/api/notifications/mark-read",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ ids })
      });
      setItems(prev => (prev||[]).map(n => ids.includes(n.id) ? {...n, read:true} : n));
      clearSelection();
    } finally { setBusy(false); }
  }

  async function markAll(){
    setBusy(true);
    try{
      await apiFetch("/api/notifications/mark-all-read",{ method:"POST" });
      setItems(prev => (prev||[]).map(n => ({...n, read:true})));
      clearSelection();
    } finally { setBusy(false); }
  }

  async function loadMore(){ if(hasMore && !busy) await load(false); }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-4" dir="rtl">
        <div className="flex items-center justify-between">
          <div className="text-xl font-semibold">اعلان‌ها</div>
          <div className="flex items-center gap-2">
            <button onClick={()=>setSelectMode(m=>!m)} className="px-3 py-1 rounded-xl border text-sm">{selectMode?"خروج از انتخاب":"انتخاب"}</button>
            <button onClick={markSelected} disabled={!Object.values(selected).some(Boolean) || busy} className="px-3 py-1 rounded-xl border text-sm disabled:opacity-50">علامت‌گذاری انتخاب‌شده</button>
            <button onClick={markAll} disabled={busy} className="px-3 py-1 rounded-xl bg-black text-white text-sm disabled:opacity-50">علامت‌گذاری همه</button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {(["all","unread","payment","ticket","automation","admin"] as Tab[]).map(t=>(
            <button key={t} onClick={()=>{ setTab(t); setOffset(0); }} className={`px-3 py-1 rounded-full text-sm border ${tab===t?"bg-black text-white":"bg-white"}`}>
              {t==="all"?"همه": t==="unread"?"خوانده‌نشده": t==="payment"?"پرداخت": t==="ticket"?"تیکت": t==="automation"?"اتوماسیون":"سیستمی"}
            </button>
          ))}
        </div>

        <div className="space-y-2 max-w-3xl">
          {items===null && (<>
            <div className="h-14 rounded-xl bg-gray-100 animate-pulse" />
            <div className="h-14 rounded-xl bg-gray-100 animate-pulse" />
          </>)}
          {items && items.length===0 && (
            <div className="text-sm opacity-70">اعلانی وجود ندارد.</div>
          )}
          {items && items.map(n=>(
            <div key={n.id} className={`rounded-xl border p-3 ${n.is_read?"opacity-70":""} flex items-start gap-3`}>
              {selectMode
                ? <input type="checkbox" checked={!!selected[n.id]} onChange={()=>toggle(n.id)} className="mt-1" />
                : <span className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100">{typeLabel(n.type)}</span>}
              <div className="min-w-0 flex-1">
                <div className="font-medium">{n.title}</div>
                {n.body && <div className="text-sm opacity-80">{n.body}</div>}
                <div className="mt-2">
                  <Link href={routeForNotification(n)} className="text-xs underline">مشاهده</Link>
                </div>
              </div>
            </div>
          ))}
        </div>

        {hasMore && (
          <div>
            <button onClick={loadMore} disabled={busy} className="px-3 py-1 rounded-xl border text-sm disabled:opacity-50">موارد بیشتر</button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}