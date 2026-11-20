import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE ? `${API_BASE}/api/v1` : '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to construct absolute media/asset URLs when needed outside apiClient
export const getFullMediaUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('blob:') || path.startsWith('data:') || path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return API_BASE ? `${API_BASE.replace(/\/+$/, '')}${cleanPath}` : cleanPath;
};

// Request interceptor: attach bearer token and normalize URL paths
apiClient.interceptors.request.use(
  (config) => {
    // Prevent duplicate /api/v1 prefix if the requested path already includes it
    if (config.url && config.url.startsWith('/api/v1/')) {
      config.url = config.url.replace(/^\/api\/v1/, '');
    }
    const token = localStorage.getItem('nutriscan_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 session expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('nutriscan_token');
      localStorage.removeItem('nutriscan_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
