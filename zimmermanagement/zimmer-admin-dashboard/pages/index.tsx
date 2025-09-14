import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import { authClient } from '../lib/auth-client';

interface DashboardStats {
  total_users: number;
  active_tickets: number;
  tokens_used: number;
  monthly_revenue: number;
}

interface RecentActivity {
  id: string;
  type: 'ticket' | 'payment' | 'user';
  message: string;
  timestamp: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    console.log('Dashboard useEffect - user:', user);
    console.log('Dashboard useEffect - authClient token:', authClient.getAccessToken());
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = authClient.getAccessToken();
      
      if (!token) {
        console.error('No access token available');
        setStats({
          total_users: 0,
          active_tickets: 0,
          tokens_used: 0,
          monthly_revenue: 0
        });
        setLoading(false);
        return;
      }
      
      // Test if backend is accessible
      try {
        const testResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'https://193.162.129.243:8000'}/api/admin/test`);
        console.log('Backend test response:', testResponse.status, await testResponse.text());
      } catch (error) {
        console.error('Backend test failed:', error);
      }
      
      // Test with auth
      try {
        const testAuthResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'https://193.162.129.243:8000'}/api/admin/test-usage-stats`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('Backend auth test response:', testAuthResponse.status, await testAuthResponse.text());
      } catch (error) {
        console.error('Backend auth test failed:', error);
      }
      
      // Fetch stats
      const statsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        console.log('Dashboard stats data:', statsData);
        setStats(statsData);
      } else {
        console.log('Dashboard stats endpoint failed, using individual endpoints');
        // Fallback to individual endpoints if dashboard stats endpoint doesn't exist
        await fetchIndividualStats();
      }

      // Fetch recent activity
      const activityResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/dashboard/activity`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setRecentActivity(activityData);
      } else {
        // Fallback to empty array if activity endpoint doesn't exist
        setRecentActivity([]);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set fallback data
      setStats({
        total_users: 0,
        active_tickets: 0,
        tokens_used: 0,
        monthly_revenue: 0
      });
      setRecentActivity([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndividualStats = async () => {
    try {
      const token = authClient.getAccessToken();
      
      if (!token) {
        console.error('No access token available for individual stats');
        setStats({
          total_users: 0,
          active_tickets: 0,
          tokens_used: 0,
          monthly_revenue: 0
        });
        return;
      }
      
      // Fetch users count
      const usersResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/users/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      // Fetch tickets count
      const ticketsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/tickets?status=open`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      // Fetch usage stats
      const usageResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      // Fetch payments for revenue
      const paymentsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || '${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://193.162.129.243:8000"}'}/api/admin/payments`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const usersData = usersResponse.ok ? await usersResponse.json() : { total_users: 0 };
      const ticketsData = ticketsResponse.ok ? await ticketsResponse.json() : { tickets: [] };
      const usageData = usageResponse.ok ? await usageResponse.json() : { tokens_used: 0 };
      const paymentsData = paymentsResponse.ok ? await paymentsResponse.json() : { payments: [] };

      console.log('Individual stats data:', {
        usersData,
        ticketsData,
        usageData,
        paymentsData
      });

      // Calculate monthly revenue
      const currentMonth = new Date().getMonth();
      const currentYear = new Date().getFullYear();
      const payments = Array.isArray(paymentsData.payments) ? paymentsData.payments : (Array.isArray(paymentsData) ? paymentsData : []);
      const monthlyRevenue = payments
        .filter((payment: any) => {
          const paymentDate = new Date(payment.date || payment.created_at);
          return paymentDate.getMonth() === currentMonth && paymentDate.getFullYear() === currentYear;
        })
        .reduce((sum: number, payment: any) => sum + (payment.amount || 0), 0);

      setStats({
        total_users: usersData.total_users || 0,
        active_tickets: Array.isArray(ticketsData.tickets) ? ticketsData.tickets.length : (Array.isArray(ticketsData) ? ticketsData.length : 0),
        tokens_used: usageData.tokens_used || 0,
        monthly_revenue: monthlyRevenue
      });

    } catch (error) {
      console.error('Error fetching individual stats:', error);
      setStats({
        total_users: 0,
        active_tickets: 0,
        tokens_used: 0,
        monthly_revenue: 0
      });
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR', {
      style: 'currency',
      currency: 'IRR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'همین الان';
    if (diffInHours < 24) return `${diffInHours} ساعت پیش`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} روز پیش`;
  };

  if (loading) {
    return (
      <Layout title="داشبورد">
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">داشبورد مدیریت</h2>
            <p className="text-gray-600 mt-2">در حال بارگذاری...</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gray-300 rounded-lg"></div>
                  <div className="mr-4">
                    <div className="h-4 bg-gray-300 rounded w-20 mb-2"></div>
                    <div className="h-6 bg-gray-300 rounded w-16"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="داشبورد">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">داشبورد مدیریت</h2>
          <p className="text-gray-600 mt-2">به پنل مدیریت زیمر خوش آمدید</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Stats Cards */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">👥</span>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">کل مشتریان</p>
                <p className="text-2xl font-semibold text-gray-900">{formatNumber(stats?.total_users || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">🎫</span>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">تیکت‌های باز</p>
                <p className="text-2xl font-semibold text-gray-900">{formatNumber(stats?.active_tickets || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">🔢</span>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">توکن‌های استفاده شده</p>
                <p className="text-2xl font-semibold text-gray-900">{formatNumber(stats?.tokens_used || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">💳</span>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-600">درآمد ماهانه</p>
                <p className="text-2xl font-semibold text-gray-900">{formatCurrency(stats?.monthly_revenue || 0)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">عملیات سریع</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <span className="text-lg mr-2">🎫</span>
              <span className="text-sm font-medium">ایجاد تیکت جدید</span>
            </button>
            <button className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <span className="text-lg mr-2">📚</span>
              <span className="text-sm font-medium">افزودن به پایگاه دانش</span>
            </button>
            <button className="flex items-center justify-center p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <span className="text-lg mr-2">👥</span>
              <span className="text-sm font-medium">مدیریت مشتریان</span>
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">فعالیت‌های اخیر</h3>
          <div className="space-y-4">
            {recentActivity.length > 0 ? (
              recentActivity.slice(0, 5).map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'ticket' ? 'bg-blue-600' :
                    activity.type === 'payment' ? 'bg-green-600' :
                    'bg-yellow-600'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">{getTimeAgo(activity.timestamp)}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>هیچ فعالیت اخیری یافت نشد</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
} 