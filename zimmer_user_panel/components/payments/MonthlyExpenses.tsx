"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { Card, Skeleton } from "@/components/Skeleton";
import { BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import { rial } from "@/lib/money";

type Point = { month: string; amount: number };

export default function MonthlyExpenses(){
  const [data,setData] = useState<Point[]|null>(null);
  const [err,setErr] = useState<string|null>(null);

  useEffect(()=>{(async()=>{
    try{
      const r = await apiFetch("/api/user/payments/monthly?months=12");
      if(!r.ok) throw new Error();
      setData(await r.json());
    }catch{ setErr("عدم دریافت هزینه‌های ماهانه"); }
  })()},[]);

  return (
    <Card className="bg-white rounded-2xl shadow-lg border-0 p-6">
      <div className="text-lg font-semibold text-gray-900 mb-4">هزینه‌های ماهانه</div>
      {!data && !err && <Skeleton className="h-64" />}
      {err && <div className="text-sm text-red-600">{err}</div>}
      {data && (
        <motion.div initial={{opacity:0}} animate={{opacity:1}}>
          <div style={{width:"100%", height:280}}>
            <ResponsiveContainer>
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="month" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#666' }}
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#666' }}
                />
                <Tooltip 
                  formatter={(v)=>`${rial(Number(v))} ریال`}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar 
                  dataKey="amount" 
                  fill="#8B5CF6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}
    </Card>
  );
}
