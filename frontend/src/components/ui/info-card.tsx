import React from 'react';

export const InfoCard: React.FC<React.HTMLAttributes<HTMLDivElement> & { title?: string }> = ({ title, children, className, ...props }) => {
  return (
    <div className={"rounded-md border p-4 bg-white dark:bg-gray-900 dark:border-gray-800 " + (className ?? '')} {...props}>
      {title ? <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-200">{title}</div> : null}
      <div className="text-sm text-gray-600 dark:text-gray-300">{children}</div>
    </div>
  );
};

InfoCard.displayName = 'InfoCard';
