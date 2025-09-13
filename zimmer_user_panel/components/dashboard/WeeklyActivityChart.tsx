"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton } from "@/components/ui/Kit";
import { BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

type Row = { day:string; tokens:number; sessions:number };

export default function WeeklyActivityChart(){
  const [data,setData]=useState<Row[]|null>(null);
  const [err,setErr]=useState<string|null>(null);
  useEffect(()=>{(async()=>{
    try{
      const r=await apiFetch("/api/user/usage?range=7d");
      if(!r.ok) throw new Error();
      const response = await r.json();
      // Handle both array and object responses
      if (Array.isArray(response)) {
        setData(response);
      } else if (response && response.recent_usage && Array.isArray(response.recent_usage)) {
        setData(response.recent_usage);
      } else {
        setData([]);
      }
    }catch{ 
      setErr("خطا در دریافت آمار هفتگی");
    }
  })()},[]);
  return (
    <Card className="col-span-12 lg:col-span-7">
      <div className="font-semibold mb-3">فعالیت هفتگی</div>
      {!data && !err && <Skeleton className="h-64" />}
      {err && <div className="text-sm text-red-600">{err}</div>}
      {data && data.length > 0 && (
        <motion.div initial={{opacity:0}} animate={{opacity:1}}>
          <div style={{width:"100%", height:260}}>
            <ResponsiveContainer>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="tokens" fill="#8B5CF6" />
                <Bar dataKey="sessions" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}
      {data && data.length === 0 && (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <div className="text-lg mb-2">📊</div>
            <div className="text-sm">داده ای برای نمایش وجود ندارد</div>
          </div>
        </div>
      )}
    </Card>
  );
}
