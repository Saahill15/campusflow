import { useEffect, useState } from 'react';
import { theme } from '../theme/theme';

const useTheme = () => {
  const [currentTheme, setCurrentTheme] = useState(theme);

  useEffect(() => {
    // Future theme switching logic can be implemented here
  }, []);

  return { theme: currentTheme, setTheme: setCurrentTheme };
};

export default useTheme;
