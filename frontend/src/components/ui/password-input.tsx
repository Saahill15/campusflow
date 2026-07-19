import React, { useState } from 'react';
import { Input, InputProps } from './input';

export const PasswordInput: React.FC<InputProps> = ({ ...props }) => {
  const [show, setShow] = useState(false);
  return (
    <div>
      <div className="relative">
        <Input {...props} type={show ? 'text' : 'password'} />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-gray-600 dark:text-gray-300"
        >
          {show ? 'Hide' : 'Show'}
        </button>
      </div>
    </div>
  );
};

PasswordInput.displayName = 'PasswordInput';
