import React from 'react';
import { cn } from './cn';

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({ label, className, children, ...props }, ref) => {
  return (
    <label className={cn('block w-full', className)}>
      {label ? <span className="text-sm mb-1 block text-gray-700 dark:text-gray-200">{label}</span> : null}
      <select ref={ref} className="w-full rounded-md border px-3 py-2 bg-white text-sm text-gray-900 dark:bg-gray-900 dark:text-gray-100" {...props}>
        {children}
      </select>
    </label>
  );
});

Select.displayName = 'Select';
