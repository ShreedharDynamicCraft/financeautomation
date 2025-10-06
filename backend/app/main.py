from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
import asyncio
from datetime import datetime

from app.config import settings, logger
from app.models import JobStatus, UploadResponse, StatusResponse
from app.llm_logic import get_data_from_llm, extract_text_from_pdf, create_excel_from_data

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    description="Professional PDF Data Extraction API with Google Gemini AI"
)

# Configure CORS
# CORS middleware - Allow all origins for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for downloads
app.mount("/downloads", StaticFiles(directory=settings.output_dir), name="downloads")

# In-memory job storage (in production, use a database)
jobs_storage = {}

async def process_pdf_background(task_id: str, file_path: str, template: str, filename: str):
    """Process PDF in the background"""
    try:
        logger.info(f"Starting PDF processing task {task_id}")
        
        # Update status to processing
        jobs_storage[task_id]["status"] = "processing"
        jobs_storage[task_id]["progress"] = 10
        
        # Step 1: Extract text from PDF
        logger.info(f"Extracting text from PDF: {file_path}")
        pdf_text = extract_text_from_pdf(file_path)
        
        if not pdf_text.strip():
            raise ValueError("No text could be extracted from the PDF file")
        
        jobs_storage[task_id]["progress"] = 40
        
        # Step 2: Process with LLM
        logger.info(f"Processing with Gemini LLM using {template}")
        extracted_data = get_data_from_llm(pdf_text, template)
        
        if not extracted_data:
            raise ValueError("No data extracted by the LLM")
        
        jobs_storage[task_id]["progress"] = 70
        
        # Step 3: Create Excel file
        logger.info("Creating Excel file from extracted data")
        output_filename = f"{task_id}_{filename.replace('.pdf', '')}_extracted.xlsx"
        output_path = Path(settings.output_dir) / output_filename
        
        excel_buffer = create_excel_from_data(extracted_data, template)
        
        # Save Excel file
        with open(output_path, 'wb') as f:
            f.write(excel_buffer.getvalue())
        
        jobs_storage[task_id]["progress"] = 100
        
        # Update job status
        download_url = f"/downloads/{output_filename}"
        jobs_storage[task_id].update({
            "status": "completed",
            "download_url": download_url,
            "completed_at": datetime.now().isoformat(),
            "progress": 100
        })
        
        # Cleanup: Remove uploaded PDF file
        try:
            Path(file_path).unlink(missing_ok=True)
            logger.info(f"Cleaned up uploaded file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not clean up file {file_path}: {e}")
        
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        
        # Update job status
        jobs_storage[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
        
        # Cleanup on failure
        try:
            Path(file_path).unlink(missing_ok=True)
        except:
            pass

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Google API key configured: {'Yes' if settings.google_api_key else 'No'}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "version": settings.version,
            "google_api": "configured" if settings.google_api_key else "not_configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template: str = Form(...)
):
    """Upload PDF file for processing"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check file size
        contents = await file.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File size exceeds {settings.max_file_size / (1024*1024):.1f}MB limit"
            )
        
        # Validate template
        if template not in ["Extraction Template 1", "Extraction Template 2"]:
            raise HTTPException(status_code=400, detail="Invalid template selection")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Save file
        file_path = Path(settings.upload_dir) / f"{task_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Store job info
        jobs_storage[task_id] = {
            "task_id": task_id,
            "filename": file.filename,
            "template": template,
            "status": "processing",
            "file_path": str(file_path),
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None,
            "download_url": None,
            "progress": 0
        }
        
        # Start background processing
        background_tasks.add_task(
            process_pdf_background,
            task_id=task_id,
            file_path=str(file_path),
            template=template,
            filename=file.filename
        )
        
        logger.info(f"Started processing task {task_id} for file {file.filename}")
        
        return UploadResponse(
            task_id=task_id,
            message="File uploaded successfully. Processing started."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get task status"""
    try:
        if task_id not in jobs_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        job = jobs_storage[task_id]
        
        return StatusResponse(
            task_id=task_id,
            status=job["status"],
            download_url=job.get("download_url"),
            error=job.get("error"),
            progress=job.get("progress")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Error checking task status")

@app.get("/api/jobs")
async def get_all_jobs():
    """Get all jobs"""
    try:
        return list(jobs_storage.values())
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving jobs")

@app.delete("/api/jobs/{task_id}")
async def cancel_job(task_id: str):
    """Cancel a job"""
    try:
        if task_id not in jobs_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update job status
        jobs_storage[task_id]["status"] = "cancelled"
        
        logger.info(f"Cancelled task {task_id}")
        return {"message": "Task cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel job error: {e}")
        raise HTTPException(status_code=500, detail="Error cancelling job")

@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download processed file"""
    try:
        file_path = Path(settings.output_dir) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Error downloading file")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )