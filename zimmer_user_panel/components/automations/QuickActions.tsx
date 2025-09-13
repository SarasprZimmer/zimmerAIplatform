"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/apiClient";
import { Card } from "@/components/Skeleton";
import { motion } from "framer-motion";

export default function QuickActions(){
  const [msg,setMsg] = useState<string | null>(null);
  const [busy,setBusy] = useState(false);

  async function openSalesTicket(){
    setBusy(true); setMsg(null);
    try{
      // Simulate ticket creation for now
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMsg("تیکت پشتیبانی فروش ثبت شد.");
      
      // TODO: Uncomment when API is ready
      // const r = await apiFetch("/api/tickets", {
      //   method:"POST",
      //   headers:{"Content-Type":"application/json"},
      //   body: JSON.stringify({ subject:"پشتیبانی فروش", category:"sales", body:"درخواست از میانبر اتوماسیون‌ها" })
      // });
      // if(!r.ok) throw new Error();
      // setMsg("تیکت پشتیبانی فروش ثبت شد.");
    }catch{ setMsg("ثبت تیکت با خطا مواجه شد."); }
    finally{ setBusy(false); }
  }

  return (
    <Card className="mb-4">
      <div className="grid md:grid-cols-3 gap-3">
        <motion.a
          href="/payment"
          className="rounded-xl border p-4 hover:bg-gray-50 block"
          initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} transition={{delay:0.02}}
        >
          <div className="font-medium">پرداخت امن</div>
          <div className="text-xs opacity-70 mt-1">درگاه امن پرداخت</div>
        </motion.a>

        <motion.a
          href="/automations/marketplace"
          className="rounded-xl border p-4 hover:bg-gray-50 block"
          initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} transition={{delay:0.05}}
        >
          <div className="font-medium">خرید اتوماسیون</div>
          <div className="text-xs opacity-70 mt-1">ثبت سفارش سریع</div>
        </motion.a>

        <motion.button
          onClick={openSalesTicket}
          className="rounded-xl border p-4 hover:bg-gray-50 text-right"
          initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} transition={{delay:0.08}}
          disabled={busy}
        >
          <div className="font-medium">پشتیبانی فروش</div>
          <div className="text-xs opacity-70 mt-1">پشتیبانی 24 ساعته</div>
          {msg && <div className="text-xs mt-2">{msg}</div>}
        </motion.button>
      </div>
    </Card>
  );
}
