import React from 'react';
import ResponsiveTable from './ResponsiveTable';

interface PaymentRecord {
  id: number;
  user_name: string;
  amount: number;
  tokens_purchased: number;
  date: string;
  method: string;
  status: string;
  transaction_id: string;
  automation_id?: number;
  automation_name?: string;
}

interface PaymentTableProps {
  records: PaymentRecord[];
  onViewTokens?: (payment: PaymentRecord) => void;
  onReportIssue?: (payment: PaymentRecord) => void;
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('fa-IR') + ' ' + date.toLocaleTimeString('fa-IR');
}

function formatCurrency(amount: number) {
  return amount.toLocaleString('fa-IR') + ' ریال';
}

function statusBadge(status: string) {
  let color = 'bg-gray-200 text-gray-700';
  if (status === 'completed') color = 'bg-green-100 text-green-800';
  else if (status === 'pending') color = 'bg-yellow-100 text-yellow-800';
  else if (status === 'failed') color = 'bg-red-100 text-red-800';
  else if (status === 'cancelled') color = 'bg-gray-100 text-gray-800';
  
  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold ${color}`}>
      {status === 'completed' ? 'موفق' : 
       status === 'pending' ? 'در انتظار' : 
       status === 'failed' ? 'ناموفق' : 
       status === 'cancelled' ? 'لغو' : status}
    </span>
  );
}

const PaymentTable: React.FC<PaymentTableProps> = ({ 
  records, 
  onViewTokens, 
  onReportIssue 
}) => {
  const columns = [
    {
      key: 'date',
      label: 'تاریخ',
      mobilePriority: true,
      render: (value: string) => formatDate(value),
      className: 'whitespace-nowrap'
    },
    {
      key: 'user_name',
      label: 'کاربر',
      mobilePriority: true,
      className: 'whitespace-nowrap'
    },
    {
      key: 'amount',
      label: 'مبلغ',
      mobilePriority: true,
      render: (value: number) => formatCurrency(value),
      className: 'text-left whitespace-nowrap'
    },
    {
      key: 'tokens_purchased',
      label: 'توکن‌ها',
      mobilePriority: true,
      className: 'text-left whitespace-nowrap'
    },
    {
      key: 'automation_name',
      label: 'اتوماسیون',
      mobilePriority: false,
      render: (value: string, row: PaymentRecord) => {
        if (row.automation_id && row.automation_name) {
          return (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-900">{row.automation_name}</span>
              {onViewTokens && (
                <button
                  onClick={() => onViewTokens(row)}
                  className="text-xs text-blue-600 hover:text-blue-800 underline"
                  title="مشاهده توکن‌های افزوده‌شده"
                >
                  مشاهده توکن‌ها
                </button>
              )}
            </div>
          );
        }
        return <span className="text-sm text-gray-500">-</span>;
      },
      className: 'whitespace-nowrap'
    },
    {
      key: 'method',
      label: 'روش پرداخت',
      mobilePriority: false,
      className: 'whitespace-nowrap'
    },
    {
      key: 'status',
      label: 'وضعیت',
      mobilePriority: true,
      render: (value: string) => statusBadge(value),
      className: 'whitespace-nowrap'
    },
    {
      key: 'transaction_id',
      label: 'شناسه تراکنش',
      mobilePriority: false,
      copyable: true,
      className: 'whitespace-nowrap'
    },
    {
      key: 'actions',
      label: 'عملیات',
      mobilePriority: true,
      render: (value: any, row: PaymentRecord) => (
        <div className="flex flex-col sm:flex-row gap-2">
          {onViewTokens && row.automation_id && (
            <button
              onClick={() => onViewTokens(row)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              مشاهده توکن‌ها
            </button>
          )}
          {onReportIssue && (
            <button
              onClick={() => onReportIssue(row)}
              className="text-xs text-red-600 hover:text-red-800 underline"
            >
              گزارش مشکل
            </button>
          )}
        </div>
      ),
      className: 'whitespace-nowrap text-sm font-medium'
    }
  ];

  return (
    <ResponsiveTable
      columns={columns}
      data={records}
      emptyMessage="هیچ پرداختی یافت نشد."
    />
  );
};

export default PaymentTable; 