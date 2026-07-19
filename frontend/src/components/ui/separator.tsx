import React from 'react';

export const Separator: React.FC<React.HTMLAttributes<HTMLHRElement>> = ({ className, ...props }) => {
  return <hr className={"my-4 border-t border-gray-200 dark:border-gray-800 " + (className ?? '')} {...props} />;
};

Separator.displayName = 'Separator';
