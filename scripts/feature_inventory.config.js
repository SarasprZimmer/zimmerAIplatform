const DESIRED_FEATURES = [
  { 
    key: "auth.profile", 
    title: "ویرایش پروفایل", 
    expectedEndpoints: ["/api/me", "/api/user/profile"] 
  },
  { 
    key: "auth.security", 
    title: "امنیت حساب (۲مرحله‌ای/ایمیل)", 
    expectedEndpoints: ["/api/auth/2fa/*", "/api/auth/verify-email"] 
  },
  { 
    key: "payments.history", 
    title: "تاریخچه پرداخت", 
    expectedEndpoints: ["/api/user/payments"] 
  },
  { 
    key: "payments.monthly", 
    title: "نمودار هزینه‌های ماهانه", 
    expectedEndpoints: ["/api/user/payments/summary", "/api/user/payments"] 
  },
  { 
    key: "payments.purchase", 
    title: "خرید اعتبار/توکن", 
    expectedEndpoints: ["/api/payments/zarinpal/init"] 
  },
  { 
    key: "discounts", 
    title: "کد تخفیف", 
    expectedEndpoints: ["/api/discounts/validate", "/api/payments/zarinpal/init"] 
  },
  { 
    key: "automations.list", 
    title: "فهرست اتوماسیون‌های من", 
    expectedEndpoints: ["/api/user/automations"] 
  },
  { 
    key: "automations.detail", 
    title: "جزئیات اتوماسیون", 
    expectedEndpoints: ["/api/automations/*"] 
  },
  { 
    key: "usage.weekly", 
    title: "مصرف هفتگی", 
    expectedEndpoints: ["/api/user/usage?range=7d"] 
  },
  { 
    key: "usage.sixMonths", 
    title: "مصرف ۶ ماه اخیر", 
    expectedEndpoints: ["/api/user/usage?range=6m"] 
  },
  { 
    key: "usage.distribution", 
    title: "توزیع مصرف بین اتوماسیون‌ها", 
    expectedEndpoints: ["/api/user/usage/distribution"] 
  },
  { 
    key: "notifications", 
    title: "اعلان‌ها", 
    expectedEndpoints: ["/api/notifications", "/api/notifications/mark-*"] 
  },
  { 
    key: "support.tickets", 
    title: "تیکت‌ها", 
    expectedEndpoints: ["/api/tickets", "/api/tickets/*/messages"] 
  },
  { 
    key: "help.docs", 
    title: "مستندات/هلپ", 
    expectedEndpoints: ["/docs", "/openapi.json"] 
  },
  { 
    key: "api.dev", 
    title: "دسترسی API/توکن‌ها", 
    expectedEndpoints: ["/api/user/automations", "/api/automation-usage"] 
  },
  { 
    key: "integrations", 
    title: "یکپارچه‌سازی‌ها/سلامت", 
    expectedEndpoints: ["/api/automations/*/health", "/api/user/automations"] 
  },
];

module.exports = { DESIRED_FEATURES };
