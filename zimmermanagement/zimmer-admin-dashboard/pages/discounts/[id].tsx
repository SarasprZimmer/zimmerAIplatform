"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import DiscountForm, { DiscountPayload } from "@/components/DiscountForm";
import { adminAPI } from "@/lib/api";
import Link from "next/link";
import Layout from "@/components/Layout";

export default function EditDiscountPage() {
  const router = useRouter();
  const { id } = router.query as { id?: string };
  const [initial, setInitial] = useState<Partial<DiscountPayload> | null>(null);

  useEffect(() => {
    if (!id) return;
    (async () => {
      const list = await adminAPI.getDiscounts();
      const found = (list || []).find((x: any) => String(x.id) === String(id));
      if (found) {
        setInitial({
          code: found.code,
          percent_off: found.percent_off,
          active: found.active,
          starts_at: found.starts_at,
          ends_at: found.ends_at,
          max_redemptions: found.max_redemptions,
          per_user_limit: found.per_user_limit,
          automation_ids: found.automation_ids || [],
        });
      }
    })();
  }, [id]);

  async function handleSubmit(data: DiscountPayload) {
    await adminAPI.updateDiscount(Number(id), data);
    router.push("/discounts");
  }

  if (!initial) return (
    <Layout title="ویرایش کد تخفیف">
      <div>در حال بارگذاری...</div>
    </Layout>
  );

  return (
    <Layout title="ویرایش کد تخفیف">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">ویرایش کد تخفیف #{id}</h1>
        <Link href="/discounts" className="underline">بازگشت</Link>
      </div>
      <DiscountForm initial={initial} onSubmit={handleSubmit} submitLabel="ذخیره تغییرات" />
    </Layout>
  );
}
