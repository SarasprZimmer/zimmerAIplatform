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
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    console.log('Dashboard useEffect - user:', user);
    console.log('Dashboard useEffect - isAuthenticated:', isAuthenticated);
    console.log('Dashboard useEffect - authClient token:', authClient.getAccessToken());

    if (user && isAuthenticated) {
      fetchDashboardData();
    } else if (!isAuthenticated) {
      console.log('User not authenticated, redirecting to login');
      // Only redirect if user is not authenticated
      window.location.href = '/login';
    }
  }, [user, isAuthenticated]);

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

      // Fetch real dashboard data from API
      const [dashboardRes, usageRes, paymentsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.zimmerai.com'}/api/admin/dashboard`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.zimmerai.com'}/api/admin/usage/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://api.zimmerai.com'}/api/admin/payments`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      const dashboardData = await dashboardRes.json();
      const usageData = await usageRes.json();
      const paymentsData = await paymentsRes.json();

      console.log('Dashboard API Response:', dashboardData);
      console.log('Usage API Response:', usageData);
      console.log('Payments API Response:', paymentsData);

      // Calculate monthly revenue from payments
      const monthlyRevenue = paymentsData.payments?.reduce((sum: number, payment: any) => {
        const paymentDate = new Date(payment.created_at || payment.date);
        const currentDate = new Date();
        const isThisMonth = paymentDate.getMonth() === currentDate.getMonth() && 
                           paymentDate.getFullYear() === currentDate.getFullYear();
        return isThisMonth ? sum + (payment.amount || 0) : sum;
      }, 0) || 0;

      setStats({
        total_users: dashboardData.data?.total_users || 0,
        active_tickets: dashboardData.data?.total_tickets || 0,
        tokens_used: usageData.total_tokens_used || 0,
        monthly_revenue: monthlyRevenue
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set fallback data on error
      setStats({
        total_users: 0,
        active_tickets: 0,
        tokens_used: 0,
        monthly_revenue: 0
      });
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Loading...">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm font-medium">U</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.total_users}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm font-medium">T</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Active Tickets</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.active_tickets}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm font-medium">K</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Tokens Used</dt>
                      <dd className="text-lg font-medium text-gray-900">{stats.tokens_used}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm font-medium">$</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Monthly Revenue</dt>
                      <dd className="text-lg font-medium text-gray-900">${stats.monthly_revenue}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
