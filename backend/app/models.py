from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    task_id: str
    message: str

class StatusResponse(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "failed"
    download_url: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = None

class JobStatus(BaseModel):
    task_id: str
    filename: str
    template: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    download_url: Optional[str] = None