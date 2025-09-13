// Mock data for saraspr1899@gmail.com
const mockPayments = [
  {
    id: 1,
    amount: 150000,
    status: "paid",
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    method: "credit_card",
    description: "اتوماسیون پاسخ دهنده ایمیل"
  },
  {
    id: 2,
    amount: 200000,
    status: "paid", 
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
    method: "bank_transfer",
    description: "پرداخت برای طرح ویژه انجام شد"
  },
  {
    id: 3,
    amount: 75000,
    status: "paid",
    created_at: new Date(Date.now() - 86400000 * 10).toISOString(),
    method: "wallet",
    description: "خرید توکن اضافی"
  },
  {
    id: 4,
    amount: 300000,
    status: "paid",
    created_at: new Date(Date.now() - 86400000 * 15).toISOString(),
    method: "credit_card",
    description: "اشتراک ماهانه"
  }
];

const mockAutomations = [
  {
    id: 1,
    name: "Travel AI",
    description: "Travel Agency ChatBot",
    tokens_remaining: 700,
    demo_tokens: 300,
    provisioned_at: new Date(Date.now() - 86400000 * 30).toISOString(),
    expiry_date: "12/22"
  },
  {
    id: 2,
    name: "Agency AI",
    description: "Agency AI Assistant", 
    tokens_remaining: 500,
    demo_tokens: 500,
    provisioned_at: new Date(Date.now() - 86400000 * 45).toISOString(),
    expiry_date: "12/22"
  },
  {
    id: 3,
    name: "Email Responder",
    description: "اتوماسیون پاسخ دهنده ایمیل",
    tokens_remaining: 200,
    demo_tokens: 800,
    provisioned_at: new Date(Date.now() - 86400000 * 60).toISOString(),
    expiry_date: "01/23"
  },
  {
    id: 4,
    name: "Data Analyzer",
    description: "تحلیلگر داده‌های هوشمند",
    tokens_remaining: 150,
    demo_tokens: 350,
    provisioned_at: new Date(Date.now() - 86400000 * 90).toISOString(),
    expiry_date: "02/23"
  }
];

const mockWeeklyUsage = [
  { day: "شنبه", tokens: 120, sessions: 80 },
  { day: "یکشنبه", tokens: 200, sessions: 150 },
  { day: "دوشنبه", tokens: 350, sessions: 250 },
  { day: "سه‌شنبه", tokens: 480, sessions: 380 },
  { day: "چهارشنبه", tokens: 180, sessions: 100 },
  { day: "پنج‌شنبه", tokens: 300, sessions: 200 },
  { day: "جمعه", tokens: 450, sessions: 350 }
];

const mockDistribution = [
  { name: "Travel AI", value: 30, color: "#8B5CF6" },
  { name: "Agency AI", value: 15, color: "#10B981" },
  { name: "Email Responder", value: 20, color: "#A855F7" },
  { name: "Data Analyzer", value: 35, color: "#C084FC" }
];

const mockSixMonthTrend = [
  { month: "فروردین", value: 300 },
  { month: "اردیبهشت", value: 500 },
  { month: "خرداد", value: 400 },
  { month: "تیر", value: 650 },
  { month: "مرداد", value: 350 },
  { month: "شهریور", value: 700 }
];

export const mockData = {
  payments: mockPayments,
  automations: mockAutomations,
  weeklyUsage: mockWeeklyUsage,
  distribution: mockDistribution,
  sixMonthTrend: mockSixMonthTrend
};
