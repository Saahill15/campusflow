import React from 'react';
import { cn } from './cn';

export const Modal: React.FC<React.PropsWithChildren<{ open: boolean; onClose: () => void; title?: string }>> = ({ open, onClose, title, children }) => {
  if (!open) return null;
  return (
    <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className={cn('relative z-10 w-full max-w-lg rounded-lg bg-white p-6 dark:bg-gray-900')}>{title ? <h3 className="text-lg font-semibold mb-2">{title}</h3> : null}{children}</div>
    </div>
  );
};

Modal.displayName = 'Modal';
