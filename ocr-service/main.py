import os
import base64
import asyncio
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.ocr_engine import extract_text_from_image, extract_text_from_pdf

load_dotenv()

app = FastAPI(
    title="LLM-Based OCR Service",
    description="Extract text from images and PDFs using Google Gemini Vision",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OCRResponse(BaseModel):
    text: str
    confidence: float
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="LLM-Based OCR Service",
        version="1.0.0"
    )


@app.post("/extract-text", response_model=OCRResponse)
async def extract_text_endpoint(
    file: UploadFile = File(...)
) -> OCRResponse:
    """
    Extract text from an uploaded image or PDF file using Google Gemini Vision.
    
    Supported formats: PNG, JPG, JPEG, PDF
    """
    # Validate file type
    allowed_types = [
        "image/png", 
        "image/jpeg", 
        "image/jpg",
        "application/pdf"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
                   f"Supported types: {', '.join(allowed_types)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file.content_type == "application/pdf":
            result = await extract_text_from_pdf(file_content)
        else:
            result = await extract_text_from_image(file_content, file.content_type)
        
        return OCRResponse(
            text=result["text"],
            confidence=result["confidence"],
            message="Text extracted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text: {str(e)}"
        )


@app.post("/extract-text-batch")
async def extract_text_batch_endpoint(
    files: list[UploadFile] = File(...)
):
    """
    Extract text from multiple images or PDFs.
    Returns an array of extraction results.
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required"
        )
    
    results = []
    
    for idx, file in enumerate(files):
        try:
            file_content = await file.read()
            
            if file.content_type == "application/pdf":
                result = await extract_text_from_pdf(file_content)
            else:
                result = await extract_text_from_image(file_content, file.content_type)
            
            results.append({
                "filename": file.filename,
                "index": idx,
                "text": result["text"],
                "confidence": result["confidence"],
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "index": idx,
                "text": "",
                "confidence": 0.0,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "total_files": len(files),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8006))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        loop="asyncio"
    )
