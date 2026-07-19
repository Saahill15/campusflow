import React from 'react';

export const SectionHeader: React.FC<{ title: string; actions?: React.ReactNode }> = ({ title, actions }) => {
  return (
    <div className="mb-4 flex items-center justify-between">
      <h2 className="text-lg font-medium text-gray-800 dark:text-gray-100">{title}</h2>
      {actions ? <div>{actions}</div> : null}
    </div>
  );
};

SectionHeader.displayName = 'SectionHeader';
