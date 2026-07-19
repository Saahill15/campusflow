import React from 'react';

export const PageHeader: React.FC<{ title: string; subtitle?: string; actions?: React.ReactNode }> = ({ title, subtitle, actions }) => {
  return (
    <div className="mb-6 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{title}</h1>
        {subtitle ? <p className="text-sm text-gray-600 dark:text-gray-300">{subtitle}</p> : null}
      </div>
      {actions ? <div className="ml-4">{actions}</div> : null}
    </div>
  );
};

PageHeader.displayName = 'PageHeader';
