import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';

const navigation = [
  { name: 'داشبورد', href: '/', icon: '📊' },
  { name: 'مشتریان', href: '/users', icon: '👥' },
  { name: 'اتوماسیون‌های کاربران', href: '/user-automations', icon: '🔧', managerOnly: true },
  { name: 'تاریخچه تنظیمات توکن', href: '/tokens/adjustments', icon: '📝', managerOnly: true },
  { name: 'پایگاه دانش', href: '/knowledge', icon: '📚' },
  { name: 'قالب‌های پایگاه دانش', href: '/kb-templates', icon: '📑' },
  { name: 'مانیتورینگ پایگاه دانش', href: '/kb-monitoring', icon: '📊' },
  { name: 'پشتیبان‌گیری', href: '/backups', icon: '📦' },
  { name: 'تیکت‌های پشتیبانی', href: '/tickets', icon: '🎫' },
  { name: 'اتوماسیون‌ها', href: '/automations', icon: '🤖' },
  { name: 'کلیدهای OpenAI', href: '/api-keys', icon: '🔑' },
  { name: 'استفاده از توکن', href: '/usage', icon: '🔢' },
  { name: 'پرداخت‌ها', href: '/payments', icon: '💳' },
  { name: 'کدهای تخفیف', href: '/discounts', icon: '🎫', managerOnly: true },
  { name: 'لاگ‌های خطا', href: '/fallbacks', icon: '⚠️' },
  { name: 'اعلان‌ها', href: '/notifications', icon: '🔔', managerOnly: true },
];

const Sidebar = () => {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen">
      <div className="p-4 sm:p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 sm:mb-6">پنل مدیریت</h2>
        
        <nav className="space-y-1 sm:space-y-2">
          {navigation.map((item) => {
            // Hide manager-only items for non-managers
            if (item.managerOnly && !user?.is_admin) {
              return null;
            }
            
            const isActive = router.pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center space-x-reverse space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar; 