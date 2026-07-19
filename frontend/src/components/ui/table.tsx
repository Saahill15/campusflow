import React from 'react';

export const DataTable = <T,>({ columns, data, className }: { columns: Array<{ key: string; title: string }>; data: T[]; className?: string }) => {
  return (
    <div className={className ?? ''}>
      <table className="w-full table-auto">
        <thead>
          <tr className="text-left text-sm text-gray-600 dark:text-gray-300">
            {columns.map((c) => (
              <th key={c.key} className="px-3 py-2">{c.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row: any, idx) => (
            <tr key={idx} className="border-t even:bg-gray-50 dark:even:bg-gray-900">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 text-sm text-gray-800 dark:text-gray-100">{row[c.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

DataTable.displayName = 'DataTable';
