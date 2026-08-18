export const getEnv = (key: string, fallback = ''): string => {
  return import.meta.env[key] ?? fallback;
};

export const resolveApiUrl = (path: string): string => {
  if (!path) return path;

  const trimmedPath = path.trim();
  if (/^https?:\/\//i.test(trimmedPath)) {
    return trimmedPath;
  }

  const baseUrl = getEnv('VITE_API_BASE_URL', '').trim().replace(/\/+$/, '');
  const normalizedPath = trimmedPath.startsWith('/') ? trimmedPath : `/${trimmedPath}`;

  if (!baseUrl) {
    return normalizedPath;
  }

  return `${baseUrl}${normalizedPath}`;
};
