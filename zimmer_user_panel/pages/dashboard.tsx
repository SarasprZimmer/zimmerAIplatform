

import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/contexts/AuthContext'
import DashboardLayout from '@/components/DashboardLayout'
import dynamic from "next/dynamic";
import RecentPayments from "@/components/dashboard/RecentPayments";
import MyAutomations from "@/components/dashboard/MyAutomations";
import { isUnderConstruction } from '@/lib/construction-config';

const WeeklyActivityChart = dynamic(()=>import("@/components/dashboard/WeeklyActivityChart"), { ssr:false });
const DistributionPie   = dynamic(()=>import("@/components/dashboard/DistributionPie"), { ssr:false });
const SixMonthTrend     = dynamic(()=>import("@/components/dashboard/SixMonthTrend"), { ssr:false });
const SupportQuick      = dynamic(()=>import("@/components/dashboard/SupportQuick"), { ssr:false });



export default function DashboardPage() {
  const { user, isAuthenticated, loading } = useAuth()
  const router = useRouter()


  useEffect(() => {
    // 🚧 UNDER CONSTRUCTION: Redirect to maintenance page
    // Change UNDER_CONSTRUCTION in construction-config.ts to false when construction is complete
    if (isUnderConstruction()) {
      router.push('/under-construction');
      return;
    }
    
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])



  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 mb-4">در حال بارگذاری...</p>
          <p className="text-sm text-gray-500 mb-6">اگر بیش از ۱۰ ثانیه طول کشید، احتمالاً مشکلی در اتصال به سرور وجود دارد</p>
          <button 
            onClick={() => router.push('/login')}
            className="btn-primary"
          >
            ورود به سیستم
          </button>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6" dir="rtl">
        
        {/* Dashboard Grid - Matching the image layout exactly */}
        <div className="grid grid-cols-12 gap-6">
          {/* Top Row */}
          <div className="col-span-12 lg:col-span-6">
            <MyAutomations />
          </div>
          <div className="col-span-12 lg:col-span-6">
            <RecentPayments />
          </div>
          
          {/* Middle Row */}
          <div className="col-span-12 lg:col-span-7">
            <WeeklyActivityChart />
          </div>
          <div className="col-span-12 lg:col-span-5">
            <DistributionPie />
          </div>
          
          {/* Bottom Row */}
          <div className="col-span-12 lg:col-span-5">
            <SupportQuick />
          </div>
          <div className="col-span-12 lg:col-span-7">
            <SixMonthTrend />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
