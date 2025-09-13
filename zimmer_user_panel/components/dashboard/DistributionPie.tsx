"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton } from "@/components/ui/Kit";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

type Slice = { name:string; value:number; color?:string };

export default function DistributionPie(){
  const [data,setData]=useState<Slice[]|null>(null);
  const [err,setErr]=useState<string|null>(null);
  useEffect(()=>{(async()=>{
    try{
      const r=await apiFetch("/api/user/usage/distribution");
      if(!r.ok) throw new Error();
      setData(await r.json());
    }catch{ 
      setErr("خطا در دریافت آمار");
    }
  })()},[]);
  return (
    <Card className="col-span-12 lg:col-span-5">
      <div className="font-semibold mb-3">آمار اتوماسیون‌ها</div>
      {!data && !err && <Skeleton className="h-64" />}
      {err && <div className="text-sm text-red-600">{err}</div>}
      {data && data.length > 0 && (
        <motion.div initial={{scale:0.97, opacity:0}} animate={{scale:1, opacity:1}}>
          <div style={{width:"100%", height:260}}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" outerRadius={100}>
                  {data.map((entry,i)=>(<Cell key={i} fill={entry.color || `hsl(${i * 60}, 70%, 50%)`} />))}
                </Pie>
                <Tooltip />
              </PieChart>
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
