import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import { adminAPI } from '../../lib/api';

interface DiscountPayload {
  code: string;
  description: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  max_uses?: number;
  is_active: boolean;
  valid_from?: string;
  valid_until?: string;
}

export default function EditDiscount() {
  const router = useRouter();
  const { id } = router.query;
  const [discount, setDiscount] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchDiscount();
    }
  }, [id]);

  async function fetchDiscount() {
    try {
      const data = await adminAPI.getDiscount(id as string);
      if (data.discounts && data.discounts.length > 0) {
        setDiscount(data.discounts[0]);
      }
    } catch (error) {
      console.error('Error fetching discount:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(data: DiscountPayload) {
    setSubmitting(true);
    try {
      await adminAPI.updateDiscount(parseInt(id as string), data);
      router.push("/discounts");
    } catch (error) {
      console.error('Error updating discount:', error);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <Layout title="Edit Discount">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading...</div>
        </div>
      </Layout>
    );
  }

  if (!discount) {
    return (
      <Layout title="Edit Discount">
        <div className="text-center py-8">
          <div className="text-red-500 text-lg">Discount not found</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Edit Discount">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Edit Discount</h1>
        
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const data: DiscountPayload = {
            code: formData.get('code') as string,
            description: formData.get('description') as string,
            discount_type: formData.get('discount_type') as 'percentage' | 'fixed',
            discount_value: Number(formData.get('discount_value')),
            max_uses: formData.get('max_uses') ? Number(formData.get('max_uses')) : undefined,
            is_active: formData.get('is_active') === 'on',
            valid_from: formData.get('valid_from') as string || undefined,
            valid_until: formData.get('valid_until') as string || undefined,
          };
          handleSubmit(data);
        }} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Code
            </label>
            <input
              type="text"
              name="code"
              defaultValue={discount.code}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              name="description"
              defaultValue={discount.description}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Discount Type
              </label>
              <select
                name="discount_type"
                defaultValue={discount.discount_type}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="percentage">Percentage</option>
                <option value="fixed">Fixed Amount</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Discount Value
              </label>
              <input
                type="number"
                name="discount_value"
                defaultValue={discount.discount_value}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Uses
            </label>
            <input
              type="number"
              name="max_uses"
              defaultValue={discount.max_uses || ''}
              min="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valid From
              </label>
              <input
                type="datetime-local"
                name="valid_from"
                defaultValue={discount.valid_from ? new Date(discount.valid_from).toISOString().slice(0, 16) : ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Valid Until
              </label>
              <input
                type="datetime-local"
                name="valid_until"
                defaultValue={discount.valid_until ? new Date(discount.valid_until).toISOString().slice(0, 16) : ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="is_active"
              defaultChecked={discount.is_active}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-700">
              Active
            </label>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => router.push('/discounts')}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {submitting ? 'Updating...' : 'Update Discount'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
