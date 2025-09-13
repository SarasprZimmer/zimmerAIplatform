import Link from "next/link";
import { adminAPI } from "@/lib/api";
import Layout from "@/components/Layout";

type Row = {
  id: number;
  user_id: number|null;
  automation_id: number|null;
  payment_id: number|null;
  code: string;
  amount_before: number;
  amount_discount: number;
  amount_after: number;
  created_at: string;
};

export async function getServerSideProps(ctx: any) {
  const id = ctx?.params?.id;
  try {
    const items: Row[] = await adminAPI.getDiscountRedemptions(Number(id));
    return { props: { id, items } };
  } catch {
    return { props: { id, items: [] } };
  }
}

export default function RedemptionsPage({ id, items }: { id: string; items: Row[] }) {
  return (
    <Layout title={`سوابق استفاده کد #${id}`}>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">سوابق استفاده کد #{id}</h1>
        <Link href="/discounts" className="underline">بازگشت</Link>
      </div>
      <div className="overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-right">کاربر</th>
              <th className="p-3 text-right">اتوماسیون</th>
              <th className="p-3 text-right">پرداخت</th>
              <th className="p-3 text-right">کد</th>
              <th className="p-3 text-right">مبلغ قبل</th>
              <th className="p-3 text-right">تخفیف</th>
              <th className="p-3 text-right">مبلغ بعد</th>
              <th className="p-3 text-right">تاریخ</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-3">#{r.user_id ?? "-"}</td>
                <td className="p-3">#{r.automation_id ?? "-"}</td>
                <td className="p-3">{r.payment_id ? <Link className="underline" href={`/payments/${r.payment_id}`}>#{r.payment_id}</Link> : "-"}</td>
                <td className="p-3 font-mono">{r.code}</td>
                <td className="p-3">{r.amount_before.toLocaleString()}</td>
                <td className="p-3">- {r.amount_discount.toLocaleString()}</td>
                <td className="p-3">{r.amount_after.toLocaleString()}</td>
                <td className="p-3">{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {!items.length && (
              <tr><td className="p-6 text-center opacity-60" colSpan={8}>موردی یافت نشد.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
