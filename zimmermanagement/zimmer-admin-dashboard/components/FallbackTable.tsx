import React, { useState } from 'react';

interface FallbackEntry {
  id: number;
  client_name: string;
  question: string;
  created_at: string;
}

interface FallbackTableProps {
  entries: FallbackEntry[];
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

const MAX_QUESTION_LENGTH = 60;

const FallbackTable: React.FC<FallbackTableProps> = ({ entries }) => {
  const [expanded, setExpanded] = useState<{ [id: number]: boolean }>({});

  const toggleExpand = (id: number) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Question</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {entries.length === 0 ? (
            <tr>
              <td colSpan={3} className="px-4 py-4 text-center text-gray-400">No fallback entries found.</td>
            </tr>
          ) : (
            entries.map((entry, idx) => (
              <tr key={entry.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-4 py-2 whitespace-nowrap font-bold">{entry.client_name}</td>
                <td className="px-4 py-2 max-w-xs">
                  {entry.question.length > MAX_QUESTION_LENGTH && !expanded[entry.id] ? (
                    <>
                      {entry.question.slice(0, MAX_QUESTION_LENGTH)}...
                      <button className="ml-2 text-blue-600 text-xs underline" onClick={() => toggleExpand(entry.id)}>
                        Show more
                      </button>
                    </>
                  ) : entry.question.length > MAX_QUESTION_LENGTH && expanded[entry.id] ? (
                    <>
                      {entry.question}
                      <button className="ml-2 text-blue-600 text-xs underline" onClick={() => toggleExpand(entry.id)}>
                        Show less
                      </button>
                    </>
                  ) : (
                    entry.question
                  )}
                </td>
                <td className="px-4 py-2 whitespace-nowrap">{formatDate(entry.created_at)}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FallbackTable; 