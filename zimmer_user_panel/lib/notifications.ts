export type NotifyType = "admin" | "ticket" | "payment" | "automation" | string;

export type Notify = {
  id: number;
  type: NotifyType;
  title: string;
  body?: string;
  data?: any;
  read: boolean;
  created_at: string;
};

export function routeForNotification(n: Notify): string {
  const d = n.data || {};
  const t = (n.type || "").toLowerCase();
  if (t === "payment") {
    return d?.payment_id ? `/payment/receipt?id=${encodeURIComponent(d.payment_id)}` : "/payment";
  }
  if (t === "ticket") {
    return d?.ticket_id ? `/support/tickets/${encodeURIComponent(d.ticket_id)}` : "/support/tickets";
  }
  if (t === "automation") {
    return d?.automation_id ? `/automations/${encodeURIComponent(d.automation_id)}` : "/automations";
  }
  return "/notifications";
}

export const TYPE_LABEL: Record<string,string> = {
  payment: "پرداخت",
  ticket: "تیکت",
  automation: "اتوماسیون",
  admin: "سیستمی",
};

export function typeLabel(t?: string) {
  return TYPE_LABEL[(t||"").toLowerCase()] || "سیستمی";
}