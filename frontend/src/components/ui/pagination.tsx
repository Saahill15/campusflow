import React from 'react';

export const Pagination: React.FC<{ current: number; total: number; onChange: (p: number) => void }> = ({ current, total, onChange }) => {
  const prev = () => onChange(Math.max(1, current - 1));
  const next = () => onChange(Math.min(total, current + 1));
  return (
    <div className="flex items-center space-x-2">
      <button onClick={prev} className="px-2 py-1 rounded border">Prev</button>
      <span className="text-sm">{current} / {total}</span>
      <button onClick={next} className="px-2 py-1 rounded border">Next</button>
    </div>
  );
};

Pagination.displayName = 'Pagination';
