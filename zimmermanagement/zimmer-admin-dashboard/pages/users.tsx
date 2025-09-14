import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { adminAPI } from '../lib/api';
import { authClient } from '../lib/auth-client';
import Layout from '../components/Layout';
import { TableSkeleton } from '../components/LoadingSkeletons';
import ResponsiveTable from '../components/ResponsiveTable';
import { toast } from '../components/Toast';

interface User {
  id: number;
  name: string;
  email: string;
  phone_number: string | null;
  role: 'manager' | 'technical_team' | 'support_staff' | 'customer';
  is_active: boolean;
  created_at: string;
}

interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  by_role: {
    managers: number;
    technical_team: number;
    support_staff: number;
    customers: number;
  };
}

interface UserFormData {
  name: string;
  email: string;
  phone_number: string;
  password?: string;
  role: 'manager' | 'technical_team' | 'support_staff' | 'customer';
}


export default function Users() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    name: '',
    email: '',
    phone_number: '',
    password: '',
    role: 'customer'
  });

  useEffect(() => {
    console.log('Users page useEffect - user:', user);
    console.log('Users page useEffect - authClient token:', authClient.getAccessToken());
    fetchUsers();
    fetchStats();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const token = authClient.getAccessToken();
      console.log('Fetching users with token:', token ? 'present' : 'missing');
      
      const params: any = {};
      if (searchTerm) params.search = searchTerm;
      if (roleFilter) params.role = roleFilter;
      if (statusFilter) params.is_active = statusFilter === 'active';
      
      console.log('Fetching users with params:', params);
      const usersData = await adminAPI.getUsers(params);
      console.log('Users data received:', usersData);
      // Handle both array and object responses
      if (Array.isArray(usersData)) {
        setUsers(usersData);
      } else if (usersData && usersData.users && Array.isArray(usersData.users)) {
        setUsers(usersData.users);
      } else {
        console.error('Unexpected users data format:', usersData);
        setUsers([]);
      }
    } catch (err: any) {
      console.error('API Error:', err);
      console.error('Error details:', err.response?.data);
      toast.error('خطا در بارگذاری کاربران');
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = authClient.getAccessToken();
      if (!token) {
        console.error('No access token available for stats');
        return;
      }
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/users/managers/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        const statsData = await response.json();
        setStats(statsData);
      } else {
        console.error('Stats fetch failed:', response.status, response.statusText);
      }
    } catch (err) {
      console.error('Stats Error:', err);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminAPI.createUser(formData);
      setShowCreateModal(false);
      resetForm();
      fetchUsers();
      fetchStats();
    } catch (err: any) {
      console.error('Create Error:', err);
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    
    try {
      const updateData = { ...formData };
      if (!updateData.password) {
        delete updateData.password; // Don't update password if empty
      }
      
      await adminAPI.updateUser(editingUser.id, updateData);
      setShowEditModal(false);
      setEditingUser(null);
      resetForm();
      fetchUsers();
      fetchStats();
    } catch (err: any) {
      console.error('Update Error:', err);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این کاربر را غیرفعال کنید؟')) return;
    
    try {
      await adminAPI.deleteUser(userId);
      fetchUsers();
      fetchStats();
    } catch (err: any) {
      console.error('Delete Error:', err);
    }
  };

  const handleActivateUser = async (userId: number) => {
    try {
      const token = authClient.getAccessToken();
      if (!token) {
        console.error('No access token available for activate user');
        return;
      }
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/users/${userId}/activate`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        toast.success('کاربر با موفقیت فعال شد');
        fetchUsers();
        fetchStats();
      }
    } catch (err: any) {
      console.error('Activate Error:', err);
      toast.error('خطا در فعال‌سازی کاربر');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone_number: '',
      password: '',
      role: 'customer'
    });
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone_number: user.phone_number || '',
      password: '',
      role: user.role
    });
    setShowEditModal(true);
  };

  const getRoleLabel = (role: string) => {
    const labels = {
      manager: 'مدیر',
      technical_team: 'تیم فنی',
      support_staff: 'پشتیبانی',
      customer: 'مشتری'
    };
    return labels[role as keyof typeof labels] || role;
  };

  const getRoleColor = (role: string) => {
    const colors = {
      manager: 'bg-red-100 text-red-800',
      technical_team: 'bg-blue-100 text-blue-800',
      support_staff: 'bg-green-100 text-green-800',
      customer: 'bg-purple-100 text-purple-800'
    };
    return colors[role as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  if (loading) {
    return (
      <Layout title="مدیریت کاربران">
        <div className="rtl">
          <TableSkeleton rows={5} columns={5} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="مدیریت کاربران">
      <div className="rtl">
        {/* Header with Stats */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-gray-900">مدیریت کاربران</h1>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              افزودن کاربر جدید
            </button>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-gray-900">{stats.total_users}</div>
                <div className="text-sm text-gray-500">کل کاربران</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-green-600">{stats.active_users}</div>
                <div className="text-sm text-gray-500">کاربران فعال</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-red-600">{stats.inactive_users}</div>
                <div className="text-sm text-gray-500">کاربران غیرفعال</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-2xl font-bold text-blue-600">{stats.by_role.managers}</div>
                <div className="text-sm text-gray-500">مدیران</div>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">جستجو</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="نام یا ایمیل..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">نقش</label>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه نقش‌ها</option>
                <option value="manager">مدیر</option>
                <option value="technical_team">تیم فنی</option>
                <option value="support_staff">پشتیبانی</option>
                <option value="customer">مشتری</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">وضعیت</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">همه وضعیت‌ها</option>
                <option value="active">فعال</option>
                <option value="inactive">غیرفعال</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchUsers}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                اعمال فیلتر
              </button>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <ResponsiveTable
            columns={[
              {
                key: 'user_info',
                label: 'کاربر',
                mobilePriority: true,
                render: (value: any, row: User) => (
                  <div>
                    <div className="text-sm font-medium text-gray-900">{row.name}</div>
                    <div className="text-sm text-gray-500">{row.email}</div>
                    {row.phone_number && (
                      <div className="text-sm text-gray-500">{row.phone_number}</div>
                    )}
                  </div>
                ),
                className: 'whitespace-nowrap'
              },
              {
                key: 'role',
                label: 'نقش',
                mobilePriority: true,
                render: (value: string) => (
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(value)}`}>
                    {getRoleLabel(value)}
                  </span>
                ),
                className: 'whitespace-nowrap'
              },
              {
                key: 'is_active',
                label: 'وضعیت',
                mobilePriority: true,
                render: (value: boolean) => (
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(value)}`}>
                    {value ? 'فعال' : 'غیرفعال'}
                  </span>
                ),
                className: 'whitespace-nowrap'
              },
              {
                key: 'created_at',
                label: 'تاریخ ایجاد',
                mobilePriority: false,
                render: (value: string) => new Date(value).toLocaleDateString('fa-IR'),
                className: 'whitespace-nowrap text-sm text-gray-500'
              },
              {
                key: 'actions',
                label: 'عملیات',
                mobilePriority: true,
                render: (value: any, row: User) => (
                  <div className="flex space-x-2 space-x-reverse">
                    <button
                      onClick={() => openEditModal(row)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      ویرایش
                    </button>
                    {row.is_active ? (
                      <button
                        onClick={() => handleDeleteUser(row.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        غیرفعال
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActivateUser(row.id)}
                        className="text-green-600 hover:text-green-800 text-sm"
                      >
                        فعال
                      </button>
                    )}
                  </div>
                ),
                className: 'whitespace-nowrap text-sm font-medium'
              }
            ]}
            data={users}
            emptyMessage="هیچ کاربری یافت نشد"
          />
        </div>

        {/* Create User Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">افزودن کاربر جدید</h2>
              <form onSubmit={handleCreateUser}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">نام</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">ایمیل</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">شماره تلفن</label>
                    <input
                      type="text"
                      value={formData.phone_number}
                      onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">رمز عبور</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">نقش</label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value as any})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="customer">مشتری</option>
                      <option value="support_staff">پشتیبانی</option>
                      <option value="technical_team">تیم فنی</option>
                      <option value="manager">مدیر</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 space-x-reverse mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    انصراف
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    ایجاد کاربر
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {showEditModal && editingUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">ویرایش کاربر</h2>
              <form onSubmit={handleUpdateUser}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">نام</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">ایمیل</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">شماره تلفن</label>
                    <input
                      type="text"
                      value={formData.phone_number}
                      onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">رمز عبور جدید (اختیاری)</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      placeholder="برای تغییر رمز عبور وارد کنید"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">نقش</label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value as any})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="customer">مشتری</option>
                      <option value="support_staff">پشتیبانی</option>
                      <option value="technical_team">تیم فنی</option>
                      <option value="manager">مدیر</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end space-x-2 space-x-reverse mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setEditingUser(null);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    انصراف
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    ذخیره تغییرات
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
