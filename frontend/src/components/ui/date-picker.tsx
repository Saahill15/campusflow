import React from 'react';
import { Input } from './input/Input';


export interface DatePickerProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const DatePicker: React.FC<DatePickerProps> = ({ label, ...props }) => {
  return (
    <label className="block w-full">
      {label ? <span className="text-sm mb-1 block text-gray-700 dark:text-gray-200">{label}</span> : null}
      <Input type="date" {...props} />
    </label>
  );
};

DatePicker.displayName = 'DatePicker';
