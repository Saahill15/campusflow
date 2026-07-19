import React from 'react';
import { Input } from './input';

export const SearchInput: React.FC<React.ComponentProps<typeof Input>> = (props) => {
  return <Input {...props} placeholder={props.placeholder ?? 'Search...'} />;
};

SearchInput.displayName = 'SearchInput';
