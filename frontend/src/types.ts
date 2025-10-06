export type JobStatus = 'processing' | 'completed' | 'failed' | 'cancelled';

export interface Job {
  taskId: string;
  filename: string;
  template: 'Extraction Template 1' | 'Extraction Template 2';
  status: JobStatus;
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
  status: JobStatus;
  download_url?: string;
  error?: string;
  progress?: number;
}

export interface ApiError {
  detail: string;
}