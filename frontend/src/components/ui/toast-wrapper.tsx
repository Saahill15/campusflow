import React from 'react';

export const ToastWrapper: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  return <div aria-live="polite" className="fixed top-4 right-4 z-50 flex flex-col gap-2">{children}</div>;
};

ToastWrapper.displayName = 'ToastWrapper';
