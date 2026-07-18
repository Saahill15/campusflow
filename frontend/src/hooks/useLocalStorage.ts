import { useCallback, useState } from 'react';
import { getLocalStorage, setLocalStorage, removeLocalStorage } from '../utils/storage';

const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    const item = getLocalStorage(key);
    return item ? (JSON.parse(item) as T) : initialValue;
  });

  const setValue = useCallback(
    (value: T) => {
      setStoredValue(value);
      setLocalStorage(key, JSON.stringify(value));
    },
    [key],
  );

  const removeValue = useCallback(() => {
    setStoredValue(initialValue);
    removeLocalStorage(key);
  }, [initialValue, key]);

  return { storedValue, setValue, removeValue };
};

export default useLocalStorage;
