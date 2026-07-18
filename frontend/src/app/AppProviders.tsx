import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '../theme/ThemeProvider';
import Router from '../routes/router';
import queryClient from '../services/query/queryClient';

const AppProviders: React.FC = () => (
  <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <Router />
    </QueryClientProvider>
  </ThemeProvider>
);

export default AppProviders;
