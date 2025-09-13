import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { apiFetch } from '@/lib/apiClient';
import DiscountCodeField from '@/components/DiscountCodeField';
import PriceSummary from '@/components/PriceSummary';
import { rial } from '@/lib/money';

interface Automation {
  id: number;
  name: string;
  description: string;
  pricing_type: string;
  price_per_token: number;
}

interface DiscountInfo {
  valid: boolean;
  code?: string;
  percent_off?: number;
  amount_before?: number;
  amount_discount?: number;
  amount_after?: number;
  reason?: string;
}

export default function PurchasePage() {
  const router = useRouter();
  const { id } = router.query;
  const [automation, setAutomation] = useState<Automation | null>(null);
  const [loading, setLoading] = useState(true);
  const [discountCode, setDiscountCode] = useState('');
  const [discountInfo, setDiscountInfo] = useState<DiscountInfo | null>(null);
  const [processing, setProcessing] = useState(false);

  const fetchAutomation = useCallback(async () => {
    try {
      const response = await apiFetch(`/api/automations/${id}`);
      const data = await response.json();
      setAutomation(data);
    } catch (error) {
      console.error('Error fetching automation:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchAutomation();
    }
  }, [id, fetchAutomation]);

  const handleDiscountValidation = async (code: string) => {
    if (!code || !automation) return;
    
    try {
      const response = await apiFetch('/api/discounts/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          automation_id: automation.id,
          amount: automation.price_per_token * 1000 // Example amount
        })
      });
      const data = await response.json();
      setDiscountInfo(data);
    } catch (error) {
      console.error('Discount validation error:', error);
      setDiscountInfo(null);
    }
  };

  const handlePurchase = async () => {
    if (!automation) return;
    
    setProcessing(true);
    try {
      const response = await apiFetch('/api/payments/zarinpal/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          automation_id: automation.id,
          amount: automation.price_per_token * 1000,
          discount_code: discountCode || null
        })
      });
      const data = await response.json();
      
      if (data.payment_url) {
        window.location.href = data.payment_url;
      }
    } catch (error) {
      console.error('Purchase error:', error);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  if (!automation) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800">اتوماسیون یافت نشد</h1>
          <button 
            onClick={() => router.back()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            بازگشت
          </button>
        </div>
      </div>
    );
  }

  const baseAmount = automation.price_per_token * 1000;
  const discountAmount = discountInfo?.amount_discount || 0;
  const finalAmount = discountInfo?.amount_after || (baseAmount - discountAmount);

  return (
    <>
      <Head>
        <title>خرید {automation.name} - پنل کاربری</title>
      </Head>
      
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-6">
              خرید {automation.name}
            </h1>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* Automation Details */}
              <div>
                <h2 className="text-lg font-semibold mb-4">جزئیات اتوماسیون</h2>
                <div className="space-y-3">
                  <p><span className="font-medium">نام:</span> {automation.name}</p>
                  <p><span className="font-medium">توضیحات:</span> {automation.description}</p>
                  <p><span className="font-medium">نوع قیمت‌گذاری:</span> {automation.pricing_type}</p>
                  <p><span className="font-medium">قیمت هر توکن:</span> {rial(automation.price_per_token)} ریال</p>
                </div>
              </div>
              
              {/* Purchase Form */}
              <div>
                <h2 className="text-lg font-semibold mb-4">فرم خرید</h2>
                
                <div className="space-y-4">
                  <DiscountCodeField
                    automationId={automation.id}
                    baseAmount={baseAmount}
                    onApplied={(res) => {
                      setDiscountCode(res.code || '');
                      setDiscountInfo(res);
                    }}
                    onCleared={() => {
                      setDiscountCode('');
                      setDiscountInfo(null);
                    }}
                  />
                  
                  <PriceSummary
                    baseAmount={baseAmount}
                    discountAmount={discountAmount}
                    finalAmount={finalAmount}
                  />
                  
                  <button
                    onClick={handlePurchase}
                    disabled={processing}
                    className="w-full bg-green-500 text-white py-3 px-6 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {processing ? 'در حال پردازش...' : 'پرداخت با زرین‌پال'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}