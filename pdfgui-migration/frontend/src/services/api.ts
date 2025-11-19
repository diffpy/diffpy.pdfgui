/**
 * API client service for backend communication.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`;
            return axios(error.config);
          }
        } catch {
          // Refresh failed, logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: (data: { email: string; password: string; first_name?: string; last_name?: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  logout: (refreshToken: string) =>
    api.post('/auth/logout', { refresh_token: refreshToken }),

  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Projects API
export const projectsApi = {
  list: (params?: { page?: number; per_page?: number; archived?: boolean; search?: string }) =>
    api.get('/projects', { params }),

  get: (id: string) =>
    api.get(`/projects/${id}`),

  create: (data: { name: string; description?: string }) =>
    api.post('/projects', data),

  update: (id: string, data: { name?: string; description?: string; is_archived?: boolean }) =>
    api.put(`/projects/${id}`, data),

  delete: (id: string) =>
    api.delete(`/projects/${id}`),
};

// Fittings API
export const fittingsApi = {
  list: (projectId: string) =>
    api.get(`/fittings/project/${projectId}`),

  get: (id: string) =>
    api.get(`/fittings/${id}`),

  create: (projectId: string, data: { name: string; copy_from?: string }) =>
    api.post(`/fittings/project/${projectId}`, data),

  run: (id: string, data: { max_iterations?: number; tolerance?: number }) =>
    api.post(`/fittings/${id}/run`, data),

  stop: (id: string) =>
    api.post(`/fittings/${id}/stop`),

  getStatus: (id: string) =>
    api.get(`/fittings/${id}/status`),

  getParameters: (id: string) =>
    api.get(`/fittings/${id}/parameters`),

  addConstraint: (id: string, data: { target: string; formula: string; phase_id?: string }) =>
    api.post(`/fittings/${id}/constraints`, data),
};

// Phases API
export const phasesApi = {
  list: (fittingId: string) =>
    api.get(`/phases/fitting/${fittingId}`),

  get: (id: string) =>
    api.get(`/phases/${id}`),

  create: (fittingId: string, data: { name: string; file_id?: string }) =>
    api.post(`/phases/fitting/${fittingId}`, data),

  updateLattice: (id: string, data: { a: number; b: number; c: number; alpha: number; beta: number; gamma: number }) =>
    api.put(`/phases/${id}/lattice`, data),

  getAtoms: (id: string) =>
    api.get(`/phases/${id}/atoms`),

  addAtom: (id: string, data: { element: string; x: number; y: number; z: number; occupancy?: number }) =>
    api.post(`/phases/${id}/atoms`, data),

  delete: (id: string) =>
    api.delete(`/phases/${id}`),
};

// Datasets API
export const datasetsApi = {
  list: (fittingId: string) =>
    api.get(`/datasets/fitting/${fittingId}`),

  get: (id: string) =>
    api.get(`/datasets/${id}`),

  create: (fittingId: string, data: { name: string; file_id?: string }) =>
    api.post(`/datasets/fitting/${fittingId}`, data),

  getData: (id: string) =>
    api.get(`/datasets/${id}/data`),

  updateInstrument: (id: string, data: { stype: string; qmax: number; qdamp: number; qbroad: number; dscale: number }) =>
    api.put(`/datasets/${id}/instrument`, data),

  updateFitRange: (id: string, data: { rmin: number; rmax: number; rstep: number }) =>
    api.put(`/datasets/${id}/fit-range`, data),

  delete: (id: string) =>
    api.delete(`/datasets/${id}`),
};

// Files API
export const filesApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: (fileType?: string) =>
    api.get('/files', { params: { file_type: fileType } }),

  get: (id: string) =>
    api.get(`/files/${id}`),

  getPreview: (id: string) =>
    api.get(`/files/${id}/preview`),

  delete: (id: string) =>
    api.delete(`/files/${id}`),
};

export default api;
