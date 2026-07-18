export const getEnv = (key: string, fallback = ''): string => {
  return import.meta.env[key] ?? fallback;
};
