import React from 'react';
import { cn } from './cn';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({ label, className, ...props }, ref) => {
  return (
    <label className={cn('block w-full', className)}>
      {label ? <span className="text-sm mb-1 block text-gray-700 dark:text-gray-200">{label}</span> : null}
      <textarea ref={ref} className="w-full rounded-md border px-3 py-2 bg-white text-sm text-gray-900 placeholder:text-gray-400 dark:bg-gray-900 dark:text-gray-100" {...props} />
    </label>
  );
});

Textarea.displayName = 'Textarea';
