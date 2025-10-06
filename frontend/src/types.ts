export interface Job {
  taskId: string;
  filename: string;
  template: 'Extraction Template 1' | 'Extraction Template 2';
  status: 'processing' | 'completed' | 'failed';
  uploadedAt: Date;
  completedAt?: Date;
  downloadUrl?: string;
  error?: string;
  progress?: number;
}

export interface UploadResponse {
  task_id: string;
  message: string;
}

export interface StatusResponse {
  task_id: string;
  status: 'processing' | 'completed' | 'failed';
  download_url?: string;
  error?: string;
  progress?: number;
}

export interface ApiError {
  detail: string;
}