"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import DashboardLayout from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton } from "@/components/ui/Kit";

export default function ReceiptPage(){
  const { query } = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const id = query.id as string | undefined;
  const [data,setData]=useState<any|null>(null);

  useEffect(()=>{(async()=>{
    if(!id || !isAuthenticated) return;
    const r = await apiFetch(`/api/user/payments/${id}`);
    setData(r.ok ? await r.json() : {});
  })()},[id, isAuthenticated]);

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
      <div className="p-6" dir="rtl">
      <div className="text-xl font-semibold mb-3">رسید پرداخت</div>
      <Card className="max-w-xl">
        {!data && <Skeleton className="h-40" />}
        {data && (
          <div className="space-y-1 text-sm">
            <div>شناسه: {data.id}</div>
            <div>مبلغ: {data.amount?.toLocaleString?.("fa-IR")} ریال</div>
            <div>توکن خریداری‌شده: {data.tokens_purchased}</div>
            <div>درگاه: {data.gateway}</div>
            <div>وضعیت: {data.status}</div>
            {data.ref_id && <div>کد پیگیری: {data.ref_id}</div>}
            {data.transaction_id && <div>تراکنش: {data.transaction_id}</div>}
            <div>تاریخ: {new Date(data.created_at).toLocaleString("fa-IR")}</div>
          </div>
        )}
      </Card>
      </div>
    </DashboardLayout>
  );
}
