import axios from 'axios';
import { UploadResponse, StatusResponse } from '../types';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for better handling of AI processing
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    } else if (error.response?.status === 413) {
      throw new Error('File size too large. Please upload a smaller file.');
    } else if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment and try again.');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    } else if (error.code === 'ERR_NETWORK') {
      throw new Error('Network error. Please check your connection.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

export const uploadFile = async (
  file: File, 
  template: 'Extraction Template 1' | 'Extraction Template 2'
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('template', template);

  try {
    const response = await api.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 180000, // 3 minutes for file upload and AI processing
    });
    
    return response.data;
  } catch (error: any) {
    console.error('Upload error:', error);
    throw error;
  }
};

export const getJobStatus = async (taskId: string): Promise<StatusResponse> => {
  try {
    const response = await api.get<StatusResponse>(`/api/status/${taskId}`);
    return response.data;
  } catch (error: any) {
    console.error('Status check error:', error);
    throw error;
  }
};

export const downloadFile = async (downloadUrl: string): Promise<Blob> => {
  try {
    // Use the API base URL if downloadUrl is relative
    const fullUrl = downloadUrl.startsWith('http') ? downloadUrl : `${API_BASE_URL}${downloadUrl}`;
    const response = await axios.get(fullUrl, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error: any) {
    console.error('Download error:', error);
    throw error;
  }
};

export const cancelJob = async (taskId: string): Promise<void> => {
  try {
    await api.delete(`/api/jobs/${taskId}`);
  } catch (error: any) {
    console.error('Cancel job error:', error);
    throw error;
  }
};

export const getAllJobs = async (): Promise<StatusResponse[]> => {
  try {
    const response = await api.get<StatusResponse[]>('/api/jobs');
    return response.data;
  } catch (error: any) {
    console.error('Get all jobs error:', error);
    throw error;
  }
};

export default api;