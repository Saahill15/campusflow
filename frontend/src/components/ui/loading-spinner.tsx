import React from 'react';

export const LoadingSpinner: React.FC<{ size?: number }> = ({ size = 24 }) => {
  return (
    <div className="flex items-center justify-center">
      <svg className="animate-spin text-gray-600 dark:text-gray-200" width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.2" />
        <path d="M22 12a10 10 0 00-10-10" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
      </svg>
    </div>
  );
};

LoadingSpinner.displayName = 'LoadingSpinner';
