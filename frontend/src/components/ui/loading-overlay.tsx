import React from 'react';
import { LoadingSpinner } from './loading-spinner';

export const LoadingOverlay: React.FC<{ visible?: boolean }> = ({ visible = true }) => {
  if (!visible) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-white/60 dark:bg-black/60">
      <LoadingSpinner size={48} />
    </div>
  );
};

LoadingOverlay.displayName = 'LoadingOverlay';
