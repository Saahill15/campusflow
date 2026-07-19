import React from 'react';
import { cn } from './cn';

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({ label, className, ...props }, ref) => {
  return (
    <label className={cn('inline-flex items-center space-x-2', className)}>
      <input ref={ref} type="checkbox" className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-800" {...props} />
      {label ? <span className="text-sm text-gray-700 dark:text-gray-200">{label}</span> : null}
    </label>
  );
});

Checkbox.displayName = 'Checkbox';
