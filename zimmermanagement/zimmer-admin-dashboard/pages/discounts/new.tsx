"use client";
import { useRouter } from "next/router";
import DiscountForm, { DiscountPayload } from "@/components/DiscountForm";
import { adminAPI } from "@/lib/api";
import Link from "next/link";
import Layout from "@/components/Layout";

export default function NewDiscountPage() {
  const router = useRouter();

  async function handleSubmit(data: DiscountPayload) {
    await adminAPI.createDiscount(data);
    router.push("/discounts");
  }

  return (
    <Layout title="تعریف کد تخفیف">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">تعریف کد تخفیف</h1>
        <Link href="/discounts" className="underline">بازگشت</Link>
      </div>
      <DiscountForm onSubmit={handleSubmit} submitLabel="ایجاد" />
    </Layout>
  );
}
