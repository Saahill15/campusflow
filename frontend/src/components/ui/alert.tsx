import React from 'react';

export const Alert: React.FC<React.PropsWithChildren<{ title?: string; variant?: 'info' | 'success' | 'warning' | 'danger' }>> = ({ title, variant = 'info', children }) => {
  const variants: Record<string, string> = {
    info: 'bg-blue-50 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    success: 'bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-200',
    warning: 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    danger: 'bg-red-50 text-red-800 dark:bg-red-900 dark:text-red-200',
  };
  return (
    <div className={"p-3 rounded-md " + variants[variant]} role="alert">
      {title ? <div className="font-semibold">{title}</div> : null}
      <div className="text-sm">{children}</div>
    </div>
  );
};

Alert.displayName = 'Alert';
