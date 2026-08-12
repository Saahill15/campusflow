import axios from 'axios';
import { getEnv } from '../../utils/env';

const baseApiUrl = getEnv('VITE_API_BASE_URL');
const baseURL = baseApiUrl
  ? `${baseApiUrl.replace(/\/$/, '')}/api/v1`
  : '/api/v1';

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    // TODO: attach JWT token when authentication is implemented
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: centralize error handling and map API errors to UI-friendly messages
    return Promise.reject(error);
  },
);

export default api;
