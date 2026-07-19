import React from 'react';

export const Progress: React.FC<{ value: number; className?: string }> = ({ value, className }) => {
  const pct = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <div className={"w-full bg-gray-200 rounded-full h-2 overflow-hidden " + (className ?? '')} role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full bg-blue-600 dark:bg-blue-500" style={{ width: `${pct}%` }} />
    </div>
  );
};

Progress.displayName = 'Progress';
