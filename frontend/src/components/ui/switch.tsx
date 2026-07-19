import React from 'react';
import { cn } from './cn';

export interface SwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  checked?: boolean;
}

export const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(({ checked, className, ...props }, ref) => {
  return (
    <label className={cn('inline-flex items-center cursor-pointer', className)}>
      <input ref={ref} type="checkbox" defaultChecked={checked} className="sr-only" {...props} />
      <span className={cn('h-5 w-9 rounded-full transition-colors', checked ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700')}> 
        <span className={cn('inline-block h-4 w-4 transform rounded-full bg-white transition-transform', checked ? 'translate-x-4' : 'translate-x-1')}></span>
      </span>
    </label>
  );
});

Switch.displayName = 'Switch';
