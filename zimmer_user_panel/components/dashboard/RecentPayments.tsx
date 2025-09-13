"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/apiClient";
import { Skeleton, Card } from "@/components/ui/Kit";

type Payment = { id:number; amount:number; status:string; created_at:string; method?:string; description?:string; };
function rial(n:number){ try{ return n.toLocaleString("fa-IR"); }catch{ return String(n); } }

export default function RecentPayments() {
  const [items,setItems]=useState<Payment[]|null>(null);
  const [err,setErr]=useState<string|null>(null);

  useEffect(()=>{(async()=>{
    try{
      const r=await apiFetch("/api/user/payments?limit=4");
      if(!r.ok) throw new Error();
      setItems(await r.json());
    }catch{ setErr("عدم دریافت اطلاعات پرداخت‌ها"); }
  })()},[]);

  return (
    <Card className="bg-white rounded-2xl shadow-lg border-0 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="text-lg font-semibold text-gray-900">پرداخت‌های اخیر</div>
        <Link href="/payment" className="text-sm text-purple-600 hover:text-purple-700 font-medium">بیشتر</Link>
      </div>
      {!items && !err && (
        <div className="space-y-3">
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
        </div>
      )}
      {err && <div className="text-sm text-red-600">{err}</div>}
      {items && items.length>0 && (
        <div className="space-y-3">
          {items.slice(0,2).map(p=>(
            <div key={p.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
              <div className="flex items-center space-x-3 space-x-reverse">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="text-sm font-medium text-gray-900">{p.description}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      {items && items.length===0 && <div className="text-sm text-gray-500">پرداختی یافت نشد.</div>}
    </Card>
  );
}
