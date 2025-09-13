import React, { useState } from 'react';
import ResponsiveTable from './ResponsiveTable';

interface KnowledgeEntry {
  id: number;
  client_name: string;
  category: string;
  answer: string;
  created_at: string;
}

interface KnowledgeTableProps {
  entries: KnowledgeEntry[];
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('fa-IR') + ' ' + date.toLocaleTimeString('fa-IR');
}

const MAX_ANSWER_LENGTH = 60;

const KnowledgeTable: React.FC<KnowledgeTableProps> = ({ entries }) => {
  const [expanded, setExpanded] = useState<{ [id: number]: boolean }>({});

  const toggleExpand = (id: number) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const renderAnswer = (answer: string, row: KnowledgeEntry) => {
    if (answer.length > MAX_ANSWER_LENGTH && !expanded[row.id]) {
      return (
        <div className="break-words">
          {answer.slice(0, MAX_ANSWER_LENGTH)}...
          <button 
            className="mr-2 text-blue-600 text-xs underline hover:text-blue-800 transition-colors"
            onClick={() => toggleExpand(row.id)}
          >
            نمایش بیشتر
          </button>
        </div>
      );
    } else if (answer.length > MAX_ANSWER_LENGTH && expanded[row.id]) {
      return (
        <div className="break-words">
          {answer}
          <button 
            className="mr-2 text-blue-600 text-xs underline hover:text-blue-800 transition-colors"
            onClick={() => toggleExpand(row.id)}
          >
            نمایش کمتر
          </button>
        </div>
      );
    }
    return <div className="break-words">{answer}</div>;
  };

  const columns = [
    {
      key: 'client_name',
      label: 'مشتری',
      mobilePriority: true,
      className: 'whitespace-nowrap'
    },
    {
      key: 'category',
      label: 'دسته‌بندی',
      mobilePriority: true,
      className: 'whitespace-nowrap'
    },
    {
      key: 'answer',
      label: 'پاسخ',
      mobilePriority: true,
      render: (value: string, row: KnowledgeEntry) => renderAnswer(value, row),
      className: 'max-w-xs'
    },
    {
      key: 'created_at',
      label: 'تاریخ ایجاد',
      mobilePriority: false,
      render: (value: string) => formatDate(value),
      className: 'whitespace-nowrap'
    }
  ];

  return (
    <ResponsiveTable
      columns={columns}
      data={entries}
      emptyMessage="هیچ ورودی دانشی یافت نشد."
    />
  );
};

export default KnowledgeTable; 