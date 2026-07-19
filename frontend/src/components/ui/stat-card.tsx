import React from 'react';

export const StatCard: React.FC<{ value: React.ReactNode; label: string; icon?: React.ReactNode }> = ({ value, label, icon }) => {
  return (
    <div className="rounded-md border p-4 bg-white dark:bg-gray-900 dark:border-gray-800">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{value}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">{label}</div>
        </div>
        {icon ? <div className="ml-4">{icon}</div> : null}
      </div>
    </div>
  );
};

StatCard.displayName = 'StatCard';
