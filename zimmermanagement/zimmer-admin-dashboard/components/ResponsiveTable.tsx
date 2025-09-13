import React from 'react';
import { toast } from './Toast';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
  className?: string;
  mobilePriority?: boolean; // Show on mobile cards
  truncate?: boolean; // Truncate long text
  copyable?: boolean; // Add copy button for long IDs
}

interface ResponsiveTableProps {
  columns: Column[];
  data: any[];
  emptyMessage?: string;
  className?: string;
}

const ResponsiveTable: React.FC<ResponsiveTableProps> = ({
  columns,
  data,
  emptyMessage = "No data found.",
  className = ""
}) => {
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('متن کپی شد');
    } catch (err) {
      console.error('Failed to copy text: ', err);
      toast.error('خطا در کپی کردن متن');
    }
  };

  const renderCell = (column: Column, value: any, row: any) => {
    if (column.render) {
      return column.render(value, row);
    }

    if (column.copyable && typeof value === 'string' && value.length > 20) {
      return (
        <div className="flex items-center gap-2">
          <span className="truncate max-w-32" title={value}>
            {value}
          </span>
          <button
            onClick={() => copyToClipboard(value)}
            className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Copy to clipboard"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      );
    }

    if (column.truncate && typeof value === 'string' && value.length > 50) {
      return (
        <span className="truncate max-w-48" title={value}>
          {value}
        </span>
      );
    }

    return value;
  };

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="mt-2 text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider ${column.className || ''}`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, idx) => (
              <tr key={row.id || idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-4 py-3 text-sm text-gray-900 ${column.className || ''}`}
                  >
                    {renderCell(column, row[column.key], row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-4">
        {data.map((row, idx) => (
          <div
            key={row.id || idx}
            className="bg-white rounded-lg border border-gray-200 p-4 space-y-3"
          >
            {columns
              .filter(column => column.mobilePriority !== false)
              .map((column) => (
                <div key={column.key} className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <dt className="text-sm font-medium text-gray-500 mb-1 sm:mb-0">
                    {column.label}:
                  </dt>
                  <dd className="text-sm text-gray-900 break-words">
                    {renderCell(column, row[column.key], row)}
                  </dd>
                </div>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResponsiveTable;
