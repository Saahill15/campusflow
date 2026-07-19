import React from 'react';

export const EmptyState: React.FC<{ title?: string; description?: string }> = ({ title = 'No data', description }) => {
  return (
    <div className="text-center py-12">
      <p className="text-lg font-semibold text-gray-700 dark:text-gray-200">{title}</p>
      {description ? <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">{description}</p> : null}
    </div>
  );
};

EmptyState.displayName = 'EmptyState';
