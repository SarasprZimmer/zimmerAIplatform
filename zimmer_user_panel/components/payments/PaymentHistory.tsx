"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton } from "@/components/Skeleton";
import { rial } from "@/lib/money";

type Row = { id:number; amount:number; status:string; created_at:string; method?:string; gateway?:string; automation_id?:number; description?:string; };

export default function PaymentHistory(){
  const [items,setItems] = useState<Row[]|null>(null);
  const [total,setTotal] = useState<number>(0);
  const [page,setPage] = useState<number>(1);
  const [limit] = useState<number>(10);
  const [err,setErr] = useState<string|null>(null);
  const pages = useMemo(()=> Math.max(1, Math.ceil((total||0)/limit)), [total,limit]);

  useEffect(()=>{(async()=>{
    setErr(null); setItems(null);
    try{
      const r = await apiFetch(`/api/user/payments?limit=${limit}&offset=${(page-1)*limit}`);
      if(!r.ok) throw new Error();
      const j = await r.json();
      if (Array.isArray(j)) {
        setItems(j); setTotal((page-1)*limit + j.length);
      } else {
        setItems(j.items || []); setTotal(j.total || (j.items?.length || 0));
      }
    }catch{ setErr("عدم دریافت تاریخچه پرداخت"); }
  })()},[page,limit]);

  return (
    <Card className="bg-white rounded-2xl shadow-lg border-0 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="text-lg font-semibold text-gray-900">پرداخت‌های اخیر</div>
        <Link href="/payment" className="text-sm text-purple-600 hover:text-purple-700 font-medium">تمام تراکنش‌ها</Link>
      </div>

      {!items && !err && (
        <div className="space-y-3">
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
          <Skeleton className="h-16" />
        </div>
      )}
      {err && <div className="text-sm text-red-600">{err}</div>}

      {items && items.length>0 && (
        <>
          <div className="overflow-hidden rounded-xl border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700 border-b border-gray-200">اتوماسیون</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700 border-b border-gray-200">تاریخ</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700 border-b border-gray-200">مبلغ</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700 border-b border-gray-200">وضعیت</th>
                </tr>
              </thead>
              <tbody>
                {items.map((p, index) => (
                  <tr key={p.id} className={`${index !== items.length - 1 ? 'border-b border-gray-100' : ''} hover:bg-gray-50 transition-colors`}>
                    <td className="px-4 py-4">
                      <div className="flex items-center">
                        <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center ml-3">
                          <svg className="w-3 h-3 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                          </svg>
                        </div>
                        <div className="text-sm font-medium text-gray-900">{p.description}</div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-gray-700">{new Date(p.created_at).toLocaleDateString('fa-IR')}</td>
                    <td className="px-4 py-4 text-sm font-semibold text-gray-900">{p.amount}</td>
                    <td className="px-4 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        p.status === 'paid' 
                          ? 'bg-green-100 text-green-800' 
                          : p.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {p.status === 'paid' ? 'پرداخت موفقیت آمیز' : p.status === 'failed' ? 'پرداخت ناموفق' : 'در حال انتظار'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="flex items-center justify-center mt-6 space-x-2 space-x-reverse">
            <button 
              disabled={page<=1} 
              onClick={()=>setPage(p=>Math.max(1,p-1))} 
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              قبلی
            </button>
            <div className="flex space-x-1 space-x-reverse">
              {[1, 2, 3, 4].map(num => (
                <button
                  key={num}
                  onClick={() => setPage(num)}
                  className={`w-8 h-8 text-sm font-medium rounded-lg transition-colors ${
                    page === num 
                      ? 'bg-purple-600 text-white' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
            <button 
              disabled={page>=pages} 
              onClick={()=>setPage(p=>p+1)} 
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              بعدی
            </button>
          </div>
        </>
      )}

      {items && items.length===0 && <div className="text-sm text-gray-500 text-center py-8">تراکنشی وجود ندارد.</div>}
    </Card>
  );
}

function faStatus(s?: string){
  switch((s||"").toLowerCase()){
    case "paid": return "موفق";
    case "failed": return "ناموفق";
    case "pending": return "در انتظار";
    default: return s || "-";
  }
}
