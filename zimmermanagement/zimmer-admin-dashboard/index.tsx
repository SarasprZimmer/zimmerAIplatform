import { useState, useEffect } from "react";
import axios from "axios";
import Layout from "./components/Layout";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
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

function AdminNotificationsPage() {
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
      }
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoadingUsers(false);
    }
  };

  return (
    <div>
      <h1>Admin Notifications Page</h1>
      <p>Welcome, {user?.name || 'Admin'}!</p>
      {/* Add your notification form here */}
    </div>
  );
}

export default function AdminNotificationsPageWithAuth() {
  return (
    <AuthProvider>
      <AdminNotificationsPage />
    </AuthProvider>
  );
}
