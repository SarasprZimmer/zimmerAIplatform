"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { Skeleton, Card } from "@/components/ui/Kit";
import { motion } from "framer-motion";

type UA = { id:number; name:string; description?:string; tokens_remaining?:number; demo_tokens?:number; provisioned_at?:string; expiry_date?:string; };

export default function MyAutomations() {
  const [items,setItems]=useState<UA[]|null>(null);
  const [err,setErr]=useState<string|null>(null);
  useEffect(()=>{(async()=>{
    try{
      const r=await apiFetch("/api/user/automations");
      if(!r.ok) throw new Error();
      setItems(await r.json());
    }catch{ setErr("عدم دریافت اتوماسیون‌ها"); }
  })()},[]);

  return (
    <Card className="bg-white rounded-2xl shadow-lg border-0 p-6">
      <div className="text-lg font-semibold text-gray-900 mb-4">اتوماسیون‌های من</div>
      {!items && !err && (
        <div className="grid grid-cols-2 gap-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      )}
      {err && <div className="text-sm text-red-600">{err}</div>}
      {items && items.length>0 && (
        <div className="grid grid-cols-2 gap-4">
          {items.slice(0,2).map((a,idx)=>(
            <motion.a
              key={a.id}
              href={`/automations/${a.id}`}
              className="rounded-xl border-2 p-4 bg-white hover:shadow-lg transition-all duration-200"
              initial={{opacity:0, y:10}}
              animate={{opacity:1, y:0}}
              transition={{delay:idx*0.05}}
            >
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center ml-3">
                  <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 text-sm">{a.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{a.description || "—"}</div>
                </div>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                <div className="h-full bg-purple-500" style={{width: `${Math.min(100, Math.round(((a.tokens_remaining||0)/((a.tokens_remaining||0)+(a.demo_tokens||0) || 1))*100))}%`}} />
              </div>
              <div className="text-xs text-gray-500">تاریخ اتمام 12/22</div>
            </motion.a>
          ))}
        </div>
      )}
      {items && items.length===0 && <div className="text-sm text-gray-500">هنوز اتوماسیونی ندارید.</div>}
    </Card>
  );
}
