import React from 'react';
import { cn } from './cn';

export interface RadioGroupProps {
  name: string;
  options: Array<{ label: string; value: string }>;
  value?: string;
  onChange?: (value: string) => void;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({ name, options, value, onChange }) => {
  return (
    <div role="radiogroup" aria-label={name} className="space-y-2">
      {options.map((opt) => (
        <label key={opt.value} className="inline-flex items-center space-x-2">
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange?.(opt.value)}
            className="h-4 w-4"
          />
          <span className="text-sm text-gray-700 dark:text-gray-200">{opt.label}</span>
        </label>
      ))}
    </div>
  );
};
