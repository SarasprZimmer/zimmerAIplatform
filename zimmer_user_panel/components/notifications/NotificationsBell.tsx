"use client";
import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/apiClient";
import { Notify, routeForNotification, typeLabel } from "@/lib/notifications";
import { motion, AnimatePresence } from "framer-motion";

const PAGE_LIMIT = 20;

export default function NotificationsBell(){
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<Notify[] | null>(null);
  const [unread, setUnread] = useState(0);
  const [busy, setBusy] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchBatch = useCallback(async (reset=false) => {
    const q = `?limit=${PAGE_LIMIT}&offset=${reset ? 0 : offset}`;
    const r = await apiFetch(`/api/notifications${q}`);
    if(!r.ok){ if(reset) setItems([]); return; }
    const j = await r.json();
    const batch: Notify[] = Array.isArray(j) ? j : (j.items || []);
    if(reset){
      setItems(batch);
      setUnread(batch.filter(x=>!x.read).length);
      setOffset(batch.length);
      setHasMore(batch.length === PAGE_LIMIT);
    }else{
      setItems(prev => [ ...(prev||[]), ...batch ]);
      setOffset(o => o + batch.length);
      setHasMore(batch.length === PAGE_LIMIT);
      setUnread(prev => {
        const newUnread = batch.filter(x=>!x.read).length;
        return prev + newUnread;
      });
    }
  }, [offset])

  const loadInitial = useCallback(async () => {
    await fetchBatch(true);
    // Try unread-count
    try {
      const c = await apiFetch("/api/notifications/unread-count");
      if(c.ok){
        const cj = await c.json();
        if(typeof cj?.count === "number") setUnread(cj.count);
      }
    } catch {}
  }, [fetchBatch])

  async function markAll(){
    setBusy(true);
    try{
      await apiFetch("/api/notifications/mark-all-read", { method:"POST" });
      // update local state
      setItems(prev => (prev||[]).map(n => ({...n, read:true})));
      setUnread(0);
    } finally { setBusy(false); }
  }

  async function markOne(id:number){
    setBusy(true);
    try{
      await apiFetch("/api/notifications/mark-read", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ ids:[id] })
      });
      setItems(prev => (prev||[]).map(n => n.id===id ? {...n, read:true} : n));
      setUnread(u => Math.max(0, u-1));
    } finally { setBusy(false); }
  }

  // realtime (SSE) with poll fallback
  useEffect(()=>{
    let closed = false;
    loadInitial();

    const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";
    let es: EventSource | null = null;

    if (typeof window !== "undefined" && API) {
      try{
        es = new EventSource(`${API.replace(/\/+$/,"")}/api/notifications/stream`, { withCredentials: true } as any);
        es.onmessage = (ev) => {
          if (closed) return;
          try{
            const data = JSON.parse(ev.data);
            setItems(prev => [data as Notify, ...(prev||[])].slice(0, PAGE_LIMIT));
            setUnread(u => u + 1);
          }catch{}
        };
        es.onerror = () => { /* ignore; polling continues */ };
      }catch{}
    }

    const poll = setInterval(()=> loadInitial(), 30000);

    const onDocClick = (e: MouseEvent) => {
      if (!dropdownRef.current) return;
      if (!dropdownRef.current.contains(e.target as any)) setOpen(false);
    };
    document.addEventListener("click", onDocClick);

    return () => {
      closed = true;
      clearInterval(poll);
      document.removeEventListener("click", onDocClick);
      try{ es?.close(); }catch{}
    };
  },[loadInitial]);

  const unreadBadge = useMemo(()=> unread>99 ? "99+" : (unread>0? String(unread):""), [unread]);

  async function loadMore(){
    if(!hasMore || loadingMore) return;
    setLoadingMore(true);
    try{ await fetchBatch(false); } finally { setLoadingMore(false); }
  }

  return (
    <div className="relative" ref={dropdownRef} dir="rtl">
      <button onClick={()=>setOpen(o=>!o)} className="relative rounded-full p-2 hover:bg-gray-100" aria-label="اعلان‌ها">
        <svg width="22" height="22" viewBox="0 0 24 24" className="fill-current"><path d="M12 2a6 6 0 00-6 6v2.586l-.707.707A1 1 0 006 14h12a1 1 0 00.707-1.707L18 10.586V8a6 6 0 00-6-6zm0 20a3 3 0 01-3-3h6a3 3 0 01-3 3z"/></svg>
        {unread>0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-red-600 text-white text-[10px] flex items-center justify-center">{unreadBadge}</span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{opacity:0,y:-6}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-6}} transition={{duration:0.15}}
            className="absolute left-0 mt-2 w-[380px] max-h-[70vh] overflow-auto rounded-2xl border bg-white shadow-lg z-50"
          >
            <div className="p-3 border-b flex items-center justify-between">
              <div className="font-medium">اعلان‌ها</div>
              <button onClick={markAll} disabled={busy || unread===0} className="text-xs underline disabled:opacity-50">علامت‌گذاری همه</button>
            </div>
            <ul className="p-2 space-y-2">
              {items === null && (<><li className="h-12 animate-pulse bg-gray-100 rounded-xl" /><li className="h-12 animate-pulse bg-gray-100 rounded-xl" /></>)}
              {items && items.length===0 && (<li className="text-sm opacity-70 p-3">اعلانی وجود ندارد.</li>)}
              {items && items.map(n=>(
                <li key={n.id} className={`rounded-xl border p-3 ${n.read?"opacity-70":""}`}>
                  <div className="flex items-start gap-3">
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-gray-100">{typeLabel(n.type)}</span>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium truncate">{n.title}</div>
                      {n.body && <div className="text-xs opacity-80 line-clamp-2">{n.body}</div>}
                      <div className="mt-2 flex items-center gap-2">
                        <Link href={routeForNotification(n)} className="text-xs underline">مشاهده</Link>
                        {!n.read && <button onClick={()=>markOne(n.id)} disabled={busy} className="text-xs underline">خواندم</button>}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            {hasMore && (
              <div className="p-2">
                <button onClick={loadMore} disabled={loadingMore} className="w-full text-sm rounded-xl border py-1 disabled:opacity-50">
                  {loadingMore ? "در حال بارگذاری..." : "موارد بیشتر"}
                </button>
              </div>
            )}
            <div className="p-2 border-t">
              <Link href="/notifications" className="block text-center text-sm underline">مشاهده همه اعلان‌ها</Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}