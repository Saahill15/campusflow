import React from 'react';
import { theme } from './theme';

interface ThemeProviderProps {
  children: React.ReactNode;
}

const ThemeProvider = ({ children }: ThemeProviderProps) => {
  return <div data-theme="campusflow">{children}</div>;
};

export { ThemeProvider };
export type { ThemeProviderProps };
export { theme };
