"use client";
import { useState } from "react";
import { useRouter } from "next/router";
import { Card } from "@/components/ui/Kit";

export default function SupportQuick(){
  const [busy,setBusy]=useState(false);
  const router = useRouter();

  async function openTicket(type:"financial"|"tech"|"customer"){
    setBusy(true);
    try{
      // Navigate to support page with pre-selected category
      await router.push(`/support?category=${type}&tab=new`);
    }catch{ 
      console.error("Navigation failed");
    }finally{ 
      setBusy(false); 
    }
  }

  return (
    <Card className="bg-white rounded-2xl shadow-lg border-0 p-6">
      <div className="text-lg font-semibold text-gray-900 mb-4">پشتیبانی</div>
      <div className="grid grid-cols-3 gap-4 mb-4">
        <button 
          onClick={()=>openTicket("financial")} 
          disabled={busy}
          className="flex flex-col items-center p-4 rounded-xl border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-2">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <span className="text-xs font-medium text-gray-700">{busy ? "..." : "پشتیبانی مالی"}</span>
        </button>
        <button 
          onClick={()=>openTicket("tech")} 
          disabled={busy}
          className="flex flex-col items-center p-4 rounded-xl border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-2">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span className="text-xs font-medium text-gray-700">{busy ? "..." : "پشتیبانی فنی"}</span>
        </button>
        <button 
          onClick={()=>openTicket("customer")} 
          disabled={busy}
          className="flex flex-col items-center p-4 rounded-xl border-2 border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-2">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <span className="text-xs font-medium text-gray-700">{busy ? "..." : "امور مشتریان"}</span>
        </button>
      </div>
      <div className="flex items-center justify-center">
        <button className="bg-purple-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors flex items-center">
          <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          ارسال
        </button>
      </div>
    </Card>
  );
}
