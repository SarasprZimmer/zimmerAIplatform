import { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../../components/Layout";
import { useAuth } from "../../contexts/AuthContext";
import { authClient } from "../../lib/auth-client";
import { adminAPI } from "../../lib/api";

const API_BASE = '${process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com"}';

interface User {
  id: number;
  name: string;
  email: string;
  phone_number: string | null;
  is_admin: boolean;
  created_at: string;
}

export default function AdminNotificationsPage() {
  const { user } = useAuth();
  const [mode, setMode] = useState<"direct"|"broadcast"|"targeted">("direct");
  const [userIds, setUserIds] = useState<string>("");
  const [type, setType] = useState("system");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [role, setRole] = useState("");
  const [data, setData] = useState<string>("");
  
  // New targeting options
  const [targetMode, setTargetMode] = useState<"all"|"username"|"email"|"active_automations">("all");
  const [targetValue, setTargetValue] = useState<string>("");
  const [users, setUsers] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);

  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState<string>("");

  // Load users for targeting
  useEffect(() => {
    if (mode === "targeted") {
      fetchUsers();
    }
  }, [mode]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const usersData = await adminAPI.getUsers();
      if (Array.isArray(usersData)) {
        setUsers(usersData);
      } else if (usersData && usersData.users && Array.isArray(usersData.users)) {
        setUsers(usersData.users);
      } else {
        setUsers([]);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const searchUsers = (query: string) => {
    if (!query.trim()) {
      setSelectedUsers([]);
      return;
    }
    
    const filtered = users.filter(u => 
      u.name.toLowerCase().includes(query.toLowerCase()) ||
      u.email.toLowerCase().includes(query.toLowerCase())
    );
    setSelectedUsers(filtered.slice(0, 10)); // Limit to 10 results
  };

  const getTargetedUserIds = (): number[] => {
    if (targetMode === "all") {
      return users.filter(u => !u.is_admin).map(u => u.id);
    } else if (targetMode === "username" || targetMode === "email") {
      return selectedUsers.map(u => u.id);
    } else if (targetMode === "active_automations") {
      // This would need to be implemented based on your automation logic
      return users.filter(u => !u.is_admin).map(u => u.id);
    }
    return [];
  };

  const loadTemplate = (template: string) => {
    switch (template) {
      case "maintenance":
        setType("system");
        setTitle("Scheduled Maintenance");
        setBody("System will be down for maintenance. We apologize for any inconvenience.");
        setData('{"maintenance_id":"maint_001","duration":"2 hours"}');
        break;
      case "update":
        setType("system");
        setTitle("System Update Available");
        setBody("New features have been deployed. Check out the latest improvements!");
        setData('{"version":"2.1.0","features":["notifications","improved-ui"]}');
        break;
      case "support":
        setType("ticket");
        setTitle("Support Ticket Updated");
        setBody("Your support ticket has received a new response.");
        setData('{"ticket_url":"/support/123"}');
        break;
      case "payment":
        setType("payment");
        setTitle("Payment Successful");
        setBody("Your payment has been processed successfully.");
        setData('{"payment_id":"pay_123","amount":100000}');
        break;
    }
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    
    if (!user || !authClient.isAuthenticated()) {
      setMsg("You must be logged in to send notifications");
      return;
    }
    
    console.log('API_BASE:', API_BASE);
    console.log('Auth token:', authClient.getAccessToken());
    console.log('User:', user);
    
    setSubmitting(true);
    setMsg("");
    try {
      if (mode === "direct") {
        const ids = userIds.split(",").map(s => s.trim()).filter(Boolean).map(Number);
        if (ids.length === 0) {
          setMsg("Please enter at least one user ID");
          return;
        }
        const payload: any = { user_ids: ids, type, title, body };
        if (data) payload.data = JSON.parse(data);
        console.log('Sending direct notification:', payload);
        const res = await axios.post(`${API_BASE}/api/admin/notifications`, payload, { 
          headers: { 'Authorization': `Bearer ${authClient.getAccessToken()}` }
        });
        setMsg(`Sent to ${res.data.created} user(s).`);
      } else if (mode === "targeted") {
        const ids = getTargetedUserIds();
        if (ids.length === 0) {
          setMsg("No users found for the selected criteria");
          return;
        }
        const payload: any = { user_ids: ids, type, title, body };
        if (data) payload.data = JSON.parse(data);
        console.log('Sending targeted notification:', payload);
        const res = await axios.post(`${API_BASE}/api/admin/notifications`, payload, { 
          headers: { 'Authorization': `Bearer ${authClient.getAccessToken()}` }
        });
        setMsg(`Sent to ${res.data.created} user(s) using ${targetMode} targeting.`);
      } else {
        const payload: any = { type, title, body };
        if (role) payload.role = role;
        if (data) payload.data = JSON.parse(data);
        console.log('Sending broadcast notification:', payload);
        const res = await axios.post(`${API_BASE}/api/admin/notifications/broadcast`, payload, { 
          headers: { 'Authorization': `Bearer ${authClient.getAccessToken()}` }
        });
        setMsg(`Broadcast created for ${res.data.created} user(s).`);
      }
      setTitle(""); setBody(""); setUserIds(""); setData(""); setRole("");
      setTargetValue(""); setSelectedUsers([]);
    } catch (err: any) {
      setMsg(err?.response?.data?.detail || "Error sending notification");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout title="اعلان‌های داخلی">
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">اعلان‌های داخلی</h1>

        <div className="bg-white rounded-2xl shadow-sm p-5 space-y-4">
        <div className="flex gap-3">
          <button className={`px-3 py-1 rounded-full ${mode==="direct"?"bg-purple-600 text-white":"bg-gray-100"}`} onClick={()=>setMode("direct")}>شناسه کاربران</button>
          <button className={`px-3 py-1 rounded-full ${mode==="targeted"?"bg-purple-600 text-white":"bg-gray-100"}`} onClick={()=>setMode("targeted")}>هدفمند</button>
          <button className={`px-3 py-1 rounded-full ${mode==="broadcast"?"bg-purple-600 text-white":"bg-gray-100"}`} onClick={()=>setMode("broadcast")}>همگانی</button>
        </div>

        <div className="border-t pt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">قالب‌های سریع</h3>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => loadTemplate("maintenance")} className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200">نگهداری</button>
            <button onClick={() => loadTemplate("update")} className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200">به‌روزرسانی سیستم</button>
            <button onClick={() => loadTemplate("support")} className="px-3 py-1 text-xs bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200">تیکت پشتیبانی</button>
            <button onClick={() => loadTemplate("payment")} className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200">پرداخت موفق</button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4">
          {mode==="direct" && (
            <div>
              <label className="text-sm text-gray-700">شناسه کاربران (جدا شده با کاما)</label>
              <input className="mt-1 w-full border rounded-xl p-2" value={userIds} onChange={e=>setUserIds(e.target.value)} placeholder="مثال: 12, 45, 98" />
              <p className="text-xs text-gray-500 mt-1">شناسه کاربران را با کاما جدا کنید</p>
            </div>
          )}
          
          {mode==="targeted" && (
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-700">روش هدف‌گیری</label>
                <select 
                  className="mt-1 w-full border rounded-xl p-2" 
                  value={targetMode} 
                  onChange={e=>setTargetMode(e.target.value as any)}
                >
                  <option value="all">همه کاربران (غیر ادمین)</option>
                  <option value="username">بر اساس نام کاربری</option>
                  <option value="email">بر اساس ایمیل</option>
                  <option value="active_automations">کاربران با اتوماسیون فعال</option>
                </select>
              </div>
              
              {(targetMode === "username" || targetMode === "email") && (
                <div>
                  <label className="text-sm text-gray-700">
                    جستجوی {targetMode === "username" ? "نام کاربری" : "ایمیل"}
                  </label>
                  <input 
                    className="mt-1 w-full border rounded-xl p-2" 
                    value={targetValue} 
                    onChange={e=>{
                      setTargetValue(e.target.value);
                      searchUsers(e.target.value);
                    }}
                    placeholder={`${targetMode === "username" ? "نام کاربری" : "ایمیل"} را وارد کنید`}
                  />
                  
                  {selectedUsers.length > 0 && (
                    <div className="mt-2 max-h-40 overflow-y-auto border rounded-lg p-2 bg-gray-50">
                      <p className="text-xs text-gray-600 mb-2">{selectedUsers.length} کاربر یافت شد:</p>
                      {selectedUsers.map(u => (
                        <div key={u.id} className="text-sm py-1 px-2 hover:bg-gray-100 rounded cursor-pointer" 
                             onClick={() => {
                               setUserIds(prev => {
                                 const ids = prev.split(",").map(s => s.trim()).filter(Boolean);
                                 if (!ids.includes(u.id.toString())) {
                                   ids.push(u.id.toString());
                                 }
                                 return ids.join(", ");
                               });
                             }}>
                          <span className="font-medium">{u.name}</span> - {u.email}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              
              {targetMode === "active_automations" && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    این گزینه همه کاربرانی که اتوماسیون فعال دارند را هدف قرار می‌دهد. 
                    {loadingUsers ? " در حال بارگذاری داده‌های کاربران..." : ` ${users.filter(u => !u.is_admin).length} کاربر غیر ادمین یافت شد.`}
                  </p>
                </div>
              )}
              
              {targetMode === "all" && (
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    این گزینه به همه کاربران غیر ادمین ارسال می‌شود.
                    {loadingUsers ? " در حال بارگذاری داده‌های کاربران..." : ` ${users.filter(u => !u.is_admin).length} کاربر غیر ادمین یافت شد.`}
                  </p>
                </div>
              )}
            </div>
          )}
          
          {mode==="broadcast" && (
            <div>
              <label className="text-sm text-gray-700">نقش (اختیاری)</label>
              <input className="mt-1 w-full border rounded-xl p-2" value={role} onChange={e=>setRole(e.target.value)} placeholder="manager | technical_team | support_staff" />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-700">نوع</label>
              <input className="mt-1 w-full border rounded-xl p-2" value={type} onChange={e=>setType(e.target.value)} placeholder="system | payment | ticket | automation" />
            </div>
            <div>
              <label className="text-sm text-gray-700">عنوان</label>
              <input className="mt-1 w-full border rounded-xl p-2" value={title} onChange={e=>setTitle(e.target.value)} required />
            </div>
          </div>

          <div>
            <label className="text-sm text-gray-700">متن</label>
            <textarea className="mt-1 w-full border rounded-xl p-2 h-28" value={body} onChange={e=>setBody(e.target.value)} />
          </div>

          <div>
            <label className="text-sm text-gray-700">داده (JSON، اختیاری)</label>
            <textarea className="mt-1 w-full border rounded-xl p-2 h-24" placeholder='{"deep_link":"/support/123"}' value={data} onChange={e=>setData(e.target.value)} />
          </div>

          <div className="flex items-center gap-3">
            <button disabled={submitting} className="px-4 py-2 rounded-xl bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50">
              {submitting ? "در حال ارسال..." : "ارسال"}
              {mode === "targeted" && !submitting && (
                <span className="ml-2 text-xs bg-purple-500 px-2 py-1 rounded">
                  {getTargetedUserIds().length} کاربر
                </span>
              )}
            </button>
            {msg && <span className="text-sm text-gray-700">{msg}</span>}
          </div>
        </form>
        </div>
      </div>
    </Layout>
  );
}
