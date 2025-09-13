'use client';

import React, { useState, useEffect } from 'react';
import { tokenAdjustmentAPI } from '../lib/api';
import { v4 as uuidv4 } from 'uuid';

interface AdjustTokensModalProps {
  isOpen: boolean;
  onClose: () => void;
  userAutomationId: number;
  automationName: string;
  userName: string;
  currentBalance: number;
  onSuccess: (newBalance: number) => void;
}

interface TokenAdjustmentPayload {
  user_automation_id: number;
  delta_tokens: number;
  reason: string;
  note?: string;
  related_payment_id?: number;
  idempotency_key?: string;
}

const REASON_OPTIONS = [
  { value: 'payment_correction', label: 'اصلاح پرداخت' },
  { value: 'promo', label: 'هدیه/تبلیغاتی' },
  { value: 'support_fix', label: 'جبران مشکل' },
  { value: 'manual', label: 'دستی' }
];

export default function AdjustTokensModal({
  isOpen,
  onClose,
  userAutomationId,
  automationName,
  userName,
  currentBalance,
  onSuccess
}: AdjustTokensModalProps) {
  const [formData, setFormData] = useState<TokenAdjustmentPayload>({
    user_automation_id: userAutomationId,
    delta_tokens: 0,
    reason: 'manual',
    note: '',
    related_payment_id: undefined,
    idempotency_key: uuidv4()
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [balance, setBalance] = useState(currentBalance);

  useEffect(() => {
    if (isOpen) {
      setBalance(currentBalance);
      setFormData(prev => ({
        ...prev,
        user_automation_id: userAutomationId,
        idempotency_key: uuidv4()
      }));
      setErrors([]);
    }
  }, [isOpen, userAutomationId, currentBalance]);

  const validateForm = (): boolean => {
    const newErrors: string[] = [];
    
    if (formData.delta_tokens === 0) {
      newErrors.push('مقدار توکن نمی‌تواند صفر باشد');
    }
    
    if (formData.delta_tokens < -10000 || formData.delta_tokens > 10000) {
      newErrors.push('مقدار توکن باید بین -10,000 تا 10,000 باشد');
    }
    
    if (!formData.reason) {
      newErrors.push('دلیل تغییر الزامی است');
    }
    
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      const response = await tokenAdjustmentAPI.postTokenAdjust(formData);
      
      // Calculate new balance
      const newBalance = balance + formData.delta_tokens;
      
      // Show success message
      // You can implement a toast system here
      alert('تغییر موجودی توکن با موفقیت ثبت شد.');
      
      // Update parent component
      onSuccess(newBalance);
      
      // Close modal
      onClose();
      
    } catch (error: any) {
      console.error('Token adjustment failed:', error);
      
      let errorMessage = 'درخواست نامعتبر. لطفاً دوباره تلاش کنید.';
      
      if (error.response?.status === 400 && error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setErrors([errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof TokenAdjustmentPayload, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear errors when user starts typing
    if (errors.length > 0) {
      setErrors([]);
    }
  };

  if (!isOpen) return null;

  const isNegativeAdjustment = formData.delta_tokens < 0;
  const newBalance = balance + formData.delta_tokens;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 rtl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 text-right">
            تنظیم موجودی توکن
          </h3>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 py-4">
          {/* Current Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 text-right mb-2">
              <span className="font-medium">اتوماسیون:</span> {automationName}
            </div>
            <div className="text-sm text-gray-600 text-right mb-2">
              <span className="font-medium">کاربر:</span> {userName}
            </div>
            <div className="text-sm text-gray-600 text-right">
              <span className="font-medium">موجودی فعلی:</span> {balance.toLocaleString()} توکن
            </div>
          </div>

          {/* Token Amount */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 text-right mb-2">
              مقدار توکن (مثبت برای افزایش، منفی برای کاهش)
            </label>
            <input
              type="number"
              value={formData.delta_tokens}
              onChange={(e) => handleInputChange('delta_tokens', parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="مثال: 50 یا -25"
              min="-10000"
              max="10000"
            />
          </div>

          {/* New Balance Preview */}
          {formData.delta_tokens !== 0 && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-800 text-right">
                <span className="font-medium">موجودی جدید:</span> {newBalance.toLocaleString()} توکن
              </div>
            </div>
          )}

          {/* Warning for negative adjustments */}
          {isNegativeAdjustment && (
            <div className="mb-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="text-sm text-yellow-800 text-right">
                ⚠️ کاهش موجودی غیرقابل بازگشت است. برای لغو باید یک افزایش معکوس ثبت کنید.
              </div>
            </div>
          )}

          {/* Reason */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 text-right mb-2">
              دلیل تغییر
            </label>
            <select
              value={formData.reason}
              onChange={(e) => handleInputChange('reason', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {REASON_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Related Payment ID */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 text-right mb-2">
              شناسه پرداخت (اختیاری)
            </label>
            <input
              type="number"
              value={formData.related_payment_id || ''}
              onChange={(e) => handleInputChange('related_payment_id', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="شناسه پرداخت مرتبط"
            />
          </div>

          {/* Note */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 text-right mb-2">
              توضیحات (اختیاری)
            </label>
            <textarea
              value={formData.note}
              onChange={(e) => handleInputChange('note', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-right focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="توضیحات اضافی..."
            />
          </div>

          {/* Error Messages */}
          {errors.length > 0 && (
            <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
              {errors.map((error, index) => (
                <div key={index} className="text-sm text-red-800 text-right">
                  {error}
                </div>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={loading || formData.delta_tokens === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'در حال ثبت...' : 'ثبت'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
