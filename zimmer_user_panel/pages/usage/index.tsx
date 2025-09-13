"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import DashboardLayout from "@/components/DashboardLayout";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton, Empty } from "@/components/ui/Kit";
import {
  ResponsiveContainer,
  BarChart, Bar,
  LineChart, Line,
  PieChart, Pie, Cell,
  CartesianGrid, XAxis, YAxis, Tooltip,
} from "recharts";

type Weekly = { day: string; tokens: number; sessions: number };
type Monthly = { month: string; value: number };
type Dist = { name: string; value: number };

export default function UsagePage(){
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [weekly,setWeekly]=useState<Weekly[]|null>(null);
  const [monthly,setMonthly]=useState<Monthly[]|null>(null);
  const [dist,setDist]=useState<Dist[]|null>(null);
  const [err,setErr]=useState<string|null>(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(()=>{(async()=>{
    if (!isAuthenticated) return;
    try{
      const w = await apiFetch("/api/user/usage?range=7d"); if (w.ok) setWeekly(await w.json()); else setWeekly([]);
      const m = await apiFetch("/api/user/usage?range=6m"); if (m.ok) setMonthly(await m.json()); else setMonthly([]);
      const d = await apiFetch("/api/user/usage/distribution"); if (d.ok) setDist(await d.json()); else setDist([]);
    }catch(e:any){ setErr("خطا در دریافت اطلاعات"); }
  })()},[isAuthenticated]);

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
      <div className="text-xl font-semibold">گزارش مصرف</div>

      <div className="grid grid-cols-12 gap-4">
        <Card className="col-span-12 lg:col-span-7">
          <div className="font-medium mb-2">فعالیت هفتگی</div>
          {!weekly && <Skeleton className="h-64" />}
          {weekly && weekly.length===0 && <Empty>داده‌ای موجود نیست.</Empty>}
          {weekly && weekly.length>0 && (
            <div style={{height:260}}>
              <ResponsiveContainer>
                <BarChart data={weekly}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="tokens" />
                  <Bar dataKey="sessions" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        <Card className="col-span-12 lg:col-span-5">
          <div className="font-medium mb-2">توزیع بین اتوماسیون‌ها</div>
          {!dist && <Skeleton className="h-64" />}
          {dist && dist.length===0 && <Empty>داده‌ای موجود نیست.</Empty>}
          {dist && dist.length>0 && (
            <div style={{height:260}}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={dist} dataKey="value" nameKey="name" outerRadius={100}>
                    {dist.map((_,i)=><Cell key={i} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        <Card className="col-span-12">
          <div className="font-medium mb-2">روند شش ماه اخیر</div>
          {!monthly && <Skeleton className="h-56" />}
          {monthly && monthly.length===0 && <Empty>داده‌ای موجود نیست.</Empty>}
          {monthly && monthly.length>0 && (
            <div style={{height:220}}>
              <ResponsiveContainer>
                <LineChart data={monthly}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </div>
      {err && <div className="text-sm text-red-600">{err}</div>}
      </div>
    </DashboardLayout>
  );
}
