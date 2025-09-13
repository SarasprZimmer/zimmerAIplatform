import React from 'react';

interface UsageRecord {
  id: number;
  date: string;
  usage_type: string;
  description?: string;
  tokens_used: number;
}

interface UsageTableProps {
  records: UsageRecord[];
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleString();
}

const UsageTable: React.FC<UsageTableProps> = ({ records }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usage Type</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Tokens Used</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {records.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-4 text-center text-gray-400">No usage records found.</td>
            </tr>
          ) : (
            records.map((record, idx) => (
              <tr key={record.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-2 whitespace-nowrap">{formatDate(record.date)}</td>
                <td className="px-4 py-2 whitespace-nowrap">{record.usage_type}</td>
                <td className="px-4 py-2 whitespace-nowrap">{record.description || '-'}</td>
                <td className="px-4 py-2 whitespace-nowrap text-right">{record.tokens_used}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default UsageTable; 