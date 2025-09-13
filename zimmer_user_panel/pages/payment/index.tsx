"use client";
import { useEffect, useMemo, useState, useCallback } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import DashboardLayout from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton, Empty } from "@/components/ui/Kit";
import {
  ResponsiveContainer,
  BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip
} from "recharts";

type Active = {
  id:number; automation_id:number; name:string; description?:string;
  tokens_remaining:number; demo_tokens:number; integration_status?:string; created_at:string;
}
type MonthPoint = { month:string; amount:number };
type PaymentRow = {
  id:number; automation_id?:number; amount:number; tokens_purchased:number;
  gateway:string; method?:string; transaction_id?:string; ref_id?:string;
  status:string; created_at:string;
};

export default function PaymentPage(){
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [active,setActive]=useState<Active[]|null>(null);
  const [months,setMonths]=useState<MonthPoint[]|null>(null);
  const [rows,setRows]=useState<PaymentRow[]|null>(null);
  const [total,setTotal]=useState(0);
  const [page,setPage]=useState(0);
  const limit = 10;

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  const load = useCallback(async () => {
    const a = await apiFetch("/api/user/automations/active");
    setActive(a.ok ? await a.json() : []);
    const s = await apiFetch("/api/user/payments/summary?months=6");
    setMonths(s.ok ? (await s.json()).points : []);
    const p = await apiFetch(`/api/user/payments?limit=${limit}&offset=${page*limit}&order=desc`);
    if(p.ok){ const j = await p.json(); setRows(j.items||[]); setTotal(j.total||0); } else { setRows([]); setTotal(0); }
  }, [page])

  useEffect(()=>{ if(isAuthenticated) load(); },[page, isAuthenticated, load]);

  const pageCount = useMemo(()=> Math.ceil((total||0)/limit), [total]);

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
      <div className="text-xl font-semibold">پرداخت‌ها و صورتحساب</div>

      {/* Active automations */}
      <Card>
        <div className="font-medium mb-2">اتوماسیون‌های فعال</div>
        {!active && <Skeleton className="h-24" />}
        {active && active.length===0 && <Empty>اتوماسیون فعالی ندارید.</Empty>}
        {active && active.length>0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {active.map(a=>(
              <div key={a.id} className="border rounded-xl p-3">
                <div className="font-medium">{a.name}</div>
                {a.description && <div className="text-sm opacity-80 line-clamp-2">{a.description}</div>}
                <div className="text-xs opacity-70 mt-2">
                  وضعیت: {a.integration_status || "-"} • توکن باقی‌مانده: {a.tokens_remaining}
                </div>
                <a href={`/automations/${a.automation_id}`} className="text-xs underline mt-2 inline-block">جزئیات</a>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Monthly expenses */}
      <Card>
        <div className="font-medium mb-2">هزینه‌های ماهانه (۶ ماه اخیر)</div>
        {!months && <Skeleton className="h-64" />}
        {months && months.length===0 && <Empty>داده‌ای موجود نیست.</Empty>}
        {months && months.length>0 && (
          <div style={{height:260}}>
            <ResponsiveContainer>
              <BarChart data={months}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="amount" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      {/* Payment history */}
      <Card>
        <div className="font-medium mb-2">تاریخچه پرداخت</div>
        {!rows && <Skeleton className="h-24" />}
        {rows && rows.length===0 && <Empty>پرداختی ثبت نشده است.</Empty>}
        {rows && rows.length>0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-right border-b">
                  <th className="py-2">تاریخ</th>
                  <th className="py-2">مبلغ</th>
                  <th className="py-2">توکن</th>
                  <th className="py-2">درگاه</th>
                  <th className="py-2">وضعیت</th>
                  <th className="py-2">رسید</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r=>(
                  <tr key={r.id} className="border-b">
                    <td className="py-2">{new Date(r.created_at).toLocaleString("fa-IR")}</td>
                    <td className="py-2">{r.amount.toLocaleString("fa-IR")} ریال</td>
                    <td className="py-2">{r.tokens_purchased}</td>
                    <td className="py-2">{r.gateway}</td>
                    <td className="py-2">{r.status}</td>
                    <td className="py-2">
                      <a href={`/payment/receipt?id=${r.id}`} className="underline">مشاهده</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex items-center justify-between mt-3">
              <div className="text-xs opacity-70">مجموع: {total}</div>
              <div className="flex items-center gap-2">
                <button disabled={page<=0} onClick={()=>setPage(p=>Math.max(0,p-1))} className="px-3 py-1 rounded-xl border disabled:opacity-50">قبلی</button>
                <div className="text-xs">صفحه {page+1} از {Math.max(1,pageCount)}</div>
                <button disabled={page+1>=pageCount} onClick={()=>setPage(p=>p+1)} className="px-3 py-1 rounded-xl border disabled:opacity-50">بعدی</button>
              </div>
            </div>
          </div>
        )}
      </Card>
      </div>
    </DashboardLayout>
  );
}
