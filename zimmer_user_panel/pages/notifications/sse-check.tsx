"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { useAuth } from "@/contexts/AuthContext";
import DashboardLayout from "@/components/DashboardLayout";

export default function SSECheck(){
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [logs,setLogs]=useState<string[]>([]);
  
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(()=>{
    const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";
    if(!API){ setLogs(l=>[...l,"NEXT_PUBLIC_API_BASE_URL not set"]); return; }
    try{
      const es = new EventSource(`${API.replace(/\/+$/,"")}/api/notifications/stream`, { withCredentials: true } as any);
      es.onmessage = ev => setLogs(l=>[...l, ev.data]);
      es.onerror = () => setLogs(l=>[...l, "error"]);
      return ()=>{ try{ es.close(); }catch{} };
    }catch(e:any){ setLogs(l=>[...l, String(e?.message||e)]) }
  },[]);

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
        <div className="text-xl font-semibold mb-4">SSE Debug - Notifications Stream</div>
        <div className="bg-gray-100 rounded-xl p-4">
          <pre className="text-xs whitespace-pre-wrap font-mono">{logs.join("\n")}</pre>
        </div>
        <div className="mt-4">
          <button 
            onClick={() => setLogs([])} 
            className="px-3 py-1 rounded-xl border text-sm"
          >
            پاک کردن لاگ‌ها
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
