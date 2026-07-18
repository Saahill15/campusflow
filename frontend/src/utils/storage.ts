const storage = typeof window !== 'undefined' ? window.localStorage : null;

export const getLocalStorage = (key: string): string | null => {
  if (!storage) return null;
  return storage.getItem(key);
};

export const setLocalStorage = (key: string, value: string): void => {
  if (!storage) return;
  storage.setItem(key, value);
};

export const removeLocalStorage = (key: string): void => {
  if (!storage) return;
  storage.removeItem(key);
};
