"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Card } from "@/components/ui/Kit";

export default function ProfileForm(){
  const { api } = useAuth();
  const [me,setMe]=useState<any|null>(null);
  const [name,setName]=useState("");
  const [phone,setPhone]=useState("");
  const [msg,setMsg]=useState<string|null>(null);
  const [busy,setBusy]=useState(false);

  useEffect(()=>{(async()=>{
    try {
      const userData = await api.getCurrentUser();
      setMe(userData);
      setName(userData?.name||"");
      setPhone(userData?.phone_number||"");
    } catch (error) {
      console.error("Failed to fetch user data:", error);
    }
  })()},[api]);

  async function saveProfile(e?:React.FormEvent){
    e?.preventDefault();
    if(!name?.trim()){ setMsg("نام را وارد کنید."); return; }
    setBusy(true); setMsg(null);
    try{
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://193.162.129.243:8000"}/api/user/profile`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ name, phone_number: phone })
      });
      setMsg(response.ok ? "تغییرات ذخیره شد." : "خطا در ذخیره‌سازی");
    } catch (error) {
      setMsg("خطا در ذخیره‌سازی");
    } finally { setBusy(false); }
  }

  return (
    <div className="max-w-2xl space-y-4" dir="rtl">
      <form onSubmit={saveProfile} className="grid md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm mb-1">نام</label>
          <input className="w-full border rounded-xl p-3" value={name} onChange={e=>setName(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm mb-1">شماره تماس</label>
          <input className="w-full border rounded-xl p-3" value={phone} onChange={e=>setPhone(e.target.value)} />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm mb-1">ایمیل</label>
          <input className="w-full border rounded-xl p-3 bg-gray-50" value={me?.email||""} disabled />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm mb-1">تاریخ عضویت</label>
          <input className="w-full border rounded-xl p-3 bg-gray-50" value={me?.created_at ? new Date(me.created_at).toLocaleDateString('fa-IR') : ''} disabled />
        </div>
        {msg && <div className="md:col-span-2 text-sm">{msg}</div>}
        <div className="md:col-span-2 flex justify-end gap-2">
          <button type="submit" disabled={busy} className="px-4 py-2 rounded-xl bg-black text-white disabled:opacity-50">ذخیره</button>
        </div>
      </form>
    </div>
  );
}