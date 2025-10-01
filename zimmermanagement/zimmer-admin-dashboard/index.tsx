import { useState, useEffect } from "react";
import axios from "axios";
import Layout from "./components/Layout";
import { useAuth } from "./contexts/AuthContext";
import { authClient } from "./lib/auth-client";
import { adminAPI } from "./lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://api.zimmerai.com";

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
        setTitle("تعمیرات سیستم");
        setBody("سیستم در حال تعمیرات است. لطفاً صبر کنید.");
        break;
      case "update":
        setType("system");
        setTitle("بروزرسانی سیستم");
        setBody("نسخه جدید سیستم منتشر شده است.");
        break;
      case "payment":
        setType("payment");
        setTitle("اطلاعیه پرداخت");
        setBody("اطلاعات مهم در مورد پرداخت‌ها");
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
          setMsg("No users selected for targeted notification");
          return;
        }
        const payload: any = { user_ids: ids, type, title, body };
        if (data) payload.data = JSON.parse(data);
        console.log('Sending targeted notification:', payload);
        const res = await axios.post(`${API_BASE}/api/admin/notifications`, payload, { 
          headers: { 'Authorization': `Bearer ${authClient.getAccessToken()}` }
        });
        setMsg(`Sent to ${res.data.created} user(s).`);
      } else if (mode === "broadcast") {
        const payload: any = { type, title, body };
        if (role) payload.role = role;
        if (data) payload.data = JSON.parse(data);
        console.log('Sending broadcast notification:', payload);
        const res = await axios.post(`${API_BASE}/api/admin/notifications/broadcast`, payload, { 
          headers: { 'Authorization': `Bearer ${authClient.getAccessToken()}` }
        });
        setMsg(`Broadcast sent to ${res.data.created} user(s).`);
      }
    } catch (error: any) {
      console.error('Error sending notification:', error);
      setMsg(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout title="ارسال اعلان">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">ارسال اعلان</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نوع ارسال
              </label>
              <select 
                value={mode} 
                onChange={e => setMode(e.target.value as any)}
                className="w-full border rounded-xl p-3"
              >
                <option value="direct">مستقیم (با ID کاربر)</option>
                <option value="targeted">هدفمند</option>
                <option value="broadcast">همه کاربران</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                قالب پیام
              </label>
              <select 
                onChange={e => loadTemplate(e.target.value)}
                className="w-full border rounded-xl p-3"
              >
                <option value="">انتخاب قالب</option>
                <option value="maintenance">تعمیرات سیستم</option>
                <option value="update">بروزرسانی</option>
                <option value="payment">پرداخت</option>
              </select>
            </div>
          </div>

          {mode === "direct" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                شناسه‌های کاربران (جدا شده با کاما)
              </label>
              <input 
                type="text" 
                value={userIds} 
                onChange={e => setUserIds(e.target.value)}
                placeholder="1,2,3,4"
                className="w-full border rounded-xl p-3"
              />
            </div>
          )}

          {mode === "targeted" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  نوع هدف‌گیری
                </label>
                <select 
                  value={targetMode} 
                  onChange={e => setTargetMode(e.target.value as any)}
                  className="w-full border rounded-xl p-3"
                >
                  <option value="all">همه کاربران غیر ادمین</option>
                  <option value="username">جستجوی نام کاربری</option>
                  <option value="email">جستجوی ایمیل</option>
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
              
            </div>
          )}

          {mode === "broadcast" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نقش کاربران (اختیاری)
              </label>
              <input 
                type="text" 
                value={role} 
                onChange={e => setRole(e.target.value)}
                placeholder="customer, admin, etc."
                className="w-full border rounded-xl p-3"
              />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نوع اعلان
              </label>
              <select 
                value={type} 
                onChange={e => setType(e.target.value)}
                className="w-full border rounded-xl p-3"
              >
                <option value="system">سیستمی</option>
                <option value="payment">پرداخت</option>
                <option value="ticket">تیکت</option>
                <option value="automation">اتوماسیون</option>
                <option value="admin">مدیریتی</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                عنوان
              </label>
              <input 
                type="text" 
                value={title} 
                onChange={e => setTitle(e.target.value)}
                placeholder="عنوان اعلان"
                className="w-full border rounded-xl p-3"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              متن پیام
            </label>
            <textarea 
              value={body} 
              onChange={e => setBody(e.target.value)}
              placeholder="متن اعلان"
              rows={4}
              className="w-full border rounded-xl p-3"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              داده اضافی (JSON - اختیاری)
            </label>
            <textarea 
              value={data} 
              onChange={e => setData(e.target.value)}
              placeholder='{"key": "value"}'
              rows={3}
              className="w-full border rounded-xl p-3 font-mono text-sm"
            />
          </div>

          <div className="flex items-center space-x-4">
            <button 
              type="submit" 
              disabled={submitting}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "در حال ارسال..." : "ارسال اعلان"}
            </button>
          </div>

          {msg && (
            <div className={`p-4 rounded-xl ${msg.includes("Error") ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>
              {msg}
            </div>
          )}
        </form>
      </div>
    </Layout>
  );
}
