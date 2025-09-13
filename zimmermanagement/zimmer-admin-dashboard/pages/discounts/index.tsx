import Link from "next/link";
import { adminAPI } from "@/lib/api";
import Layout from "@/components/Layout";

type Row = {
  id: number; code: string; percent_off: number; active: boolean;
  starts_at?: string|null; ends_at?: string|null;
  max_redemptions?: number|null; per_user_limit?: number|null;
  automation_ids: number[];
};

export async function getServerSideProps() {
  try {
    const items: Row[] = await adminAPI.getDiscounts();
    return { props: { items } };
  } catch {
    return { props: { items: [] } };
  }
}

export default function DiscountsList({ items }: { items: Row[] }) {
  return (
    <Layout title="کدهای تخفیف">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">کدهای تخفیف</h1>
        <Link href="/discounts/new" className="px-4 py-2 rounded-xl bg-black text-white">تعریف کد جدید</Link>
      </div>
      <div className="overflow-auto rounded-2xl border">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-3 text-right">کد</th>
              <th className="p-3 text-right">% تخفیف</th>
              <th className="p-3 text-right">وضعیت</th>
              <th className="p-3 text-right">بازه</th>
              <th className="p-3 text-right">محدودیت‌ها</th>
              <th className="p-3 text-right">اعمال روی</th>
              <th className="p-3 text-right">اقدامات</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id} className="border-t">
                <td className="p-3 font-mono">{r.code}</td>
                <td className="p-3">{r.percent_off}%</td>
                <td className="p-3">{r.active ? "فعال" : "غیرفعال"}</td>
                <td className="p-3">
                  {r.starts_at ? new Date(r.starts_at).toLocaleString() : "-"} → {r.ends_at ? new Date(r.ends_at).toLocaleString() : "-"}
                </td>
                <td className="p-3">
                  کل: {r.max_redemptions ?? "-"} / هر کاربر: {r.per_user_limit ?? "-"}
                </td>
                <td className="p-3">
                  {r.automation_ids?.length ? `${r.automation_ids.length} مورد` : "همه"}
                </td>
                <td className="p-3">
                  <div className="flex gap-2">
                    <Link href={`/discounts/${r.id}`} className="underline">ویرایش</Link>
                    <Link href={`/discounts/${r.id}/redemptions`} className="underline">سوابق</Link>
                  </div>
                </td>
              </tr>
            ))}
            {!items.length && (
              <tr><td className="p-6 text-center opacity-60" colSpan={7}>موردی یافت نشد.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
