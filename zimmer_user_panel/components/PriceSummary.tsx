import { rial } from "@/lib/money";

export default function PriceSummary({
  baseAmount, discountAmount, finalAmount
}: { baseAmount: number; discountAmount?: number; finalAmount?: number; }) {
  const disc = discountAmount || 0;
  const after = finalAmount ?? (baseAmount - disc);
  return (
    <div className="border rounded-2xl p-4 space-y-2">
      <div className="flex justify-between"><span>مبلغ اولیه</span><span className="font-medium">{rial(baseAmount)} ریال</span></div>
      <div className="flex justify-between"><span>تخفیف</span><span className="font-medium">− {rial(disc)} ریال</span></div>
      <div className="border-t pt-2 flex justify-between text-lg">
        <span>مبلغ نهایی</span><span className="font-semibold">{rial(after)} ریال</span>
      </div>
    </div>
  );
}
