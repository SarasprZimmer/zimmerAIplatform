# Zimmer AI User Panel

پنل کاربری اتوماسیون هوشمند Zimmer AI با استفاده از Next.js 15، TailwindCSS 4 و پشتیبانی کامل از RTL (فارسی).

## ویژگی‌ها

✅ **تکنولوژی‌های استفاده شده:**
- Next.js 15+ (App Router)
- TailwindCSS 4
- TypeScript
- RTL Layout با فونت Vazirmatn
- JWT Authentication (ذخیره در کوکی‌ها)

✅ **ساختار پنل:**
- Sidebar با ناوبری کامل
- Topbar با اطلاعات کاربر
- Layout ریسپانسیو
- پشتیبانی کامل از موبایل

✅ **صفحات موجود:**
- داشبورد (`/dashboard`) - با آمار استفاده از توکن و لیست اتوماسیون‌ها
- اتوماسیون‌ها (`/automation`) - صفحه در حال توسعه
- پرداخت‌ها (`/payment`) - صفحه در حال توسعه
- پشتیبانی (`/support`) - صفحه در حال توسعه
- تنظیمات (`/settings`) - صفحه در حال توسعه
- ورود (`/login`) - صفحه placeholder

## نصب و راه‌اندازی

### پیش‌نیازها
- Node.js 18+ 
- npm یا yarn

### مراحل نصب

1. **کلون کردن پروژه:**
```bash
git clone <repository-url>
cd zimmer_user_panel
```

2. **نصب وابستگی‌ها:**
```bash
npm install
# یا
yarn install
```

3. **اجرای پروژه در حالت توسعه:**
```bash
npm run dev
# یا
yarn dev
```

4. **باز کردن مرورگر:**
```
http://localhost:3000
```

## ساختار پروژه

```
zimmer_user_panel/
├── app/                          # Next.js App Router
│   ├── dashboard/                # صفحه داشبورد
│   ├── automation/               # صفحه اتوماسیون‌ها
│   ├── payment/                  # صفحه پرداخت‌ها
│   ├── support/                  # صفحه پشتیبانی
│   ├── settings/                 # صفحه تنظیمات
│   ├── login/                    # صفحه ورود
│   ├── globals.css              # استایل‌های全局
│   ├── layout.tsx               # Layout اصلی
│   └── page.tsx                 # صفحه اصلی (redirect)
├── components/                   # کامپوننت‌های قابل استفاده مجدد
│   ├── DashboardLayout.tsx      # Layout داشبورد
│   ├── Sidebar.tsx              # Sidebar ناوبری
│   ├── Topbar.tsx               # Topbar اطلاعات کاربر
│   └── dashboard/               # کامپوننت‌های داشبورد
│       ├── TokenUsageCard.tsx   # کارت استفاده از توکن
│       ├── PurchasedAutomationsCard.tsx  # کارت اتوماسیون‌های خریداری شده
│       └── AvailableAutomationsCard.tsx  # کارت اتوماسیون‌های موجود
├── lib/                         # توابع و تایپ‌های مشترک
│   ├── auth.ts                  # توابع احراز هویت
│   └── mockData.ts              # داده‌های نمونه
├── package.json                 # وابستگی‌ها و اسکریپت‌ها
├── tailwind.config.js           # تنظیمات TailwindCSS
├── next.config.js               # تنظیمات Next.js
└── tsconfig.json                # تنظیمات TypeScript
```

## احراز هویت

پروژه از JWT برای احراز هویت استفاده می‌کند:

- توکن‌ها در کوکی‌ها ذخیره می‌شوند
- بررسی خودکار اعتبار توکن در هر صفحه
- ریدایرکت خودکار به صفحه ورود در صورت عدم احراز هویت

### برای تست:
- از دکمه "ورود به عنوان کاربر نمونه" در صفحه ورود استفاده کنید
- یا مستقیماً به `/dashboard` بروید

## استایل‌دهی

- **TailwindCSS 4** برای استایل‌دهی
- **فونت Vazirmatn** برای نمایش بهتر متون فارسی
- **RTL Layout** کامل
- **کامپوننت‌های سفارشی** برای دکمه‌ها، کارت‌ها و آیتم‌های sidebar

## کامپوننت‌های سفارشی

### کلاس‌های CSS سفارشی:
- `.sidebar-item` - آیتم‌های sidebar
- `.card` - کارت‌های محتوا
- `.btn-primary` - دکمه‌های اصلی
- `.btn-secondary` - دکمه‌های ثانویه

## توسعه

### اضافه کردن صفحه جدید:
1. پوشه جدید در `app/` ایجاد کنید
2. فایل `page.tsx` با ساختار مشابه صفحات موجود
3. از `DashboardLayout` استفاده کنید
4. مسیر را به sidebar اضافه کنید

### اضافه کردن کامپوننت جدید:
1. فایل جدید در `components/` ایجاد کنید
2. از TypeScript interfaces استفاده کنید
3. از TailwindCSS برای استایل‌دهی استفاده کنید

## اسکریپت‌های موجود

```bash
npm run dev      # اجرای سرور توسعه
npm run build    # ساخت پروژه برای production
npm run start    # اجرای سرور production
npm run lint     # بررسی کد با ESLint
```

## نکات مهم

- تمام متون به فارسی نوشته شده‌اند
- Layout کاملاً RTL است
- پشتیبانی کامل از موبایل
- استفاده از mock data برای نمایش
- آماده برای اتصال به API واقعی

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. 