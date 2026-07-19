import React from 'react';

export const TableToolbar: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => {
  return (
    <div className={"flex items-center justify-between space-x-4 py-2 " + (className ?? '')} {...props}>
      {children}
    </div>
  );
};

TableToolbar.displayName = 'TableToolbar';
