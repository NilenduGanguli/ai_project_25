import asyncio
import os
import re
import tempfile
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.schemas.response_models import AnalysisResponse, HealthResponse, AnalysisMode
from src.utils.analyzer import analyze_pdf, query_vector_store, ingest_pdf_to_vector_store
from src.utils.utils import _validate_file_async, _save_uploaded_file_async, _cleanup_temp_files_async

load_dotenv()

app = FastAPI(
    title="PDF Analyzer API",
    description="Analyze PDF files and query them",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    k: int = 4

@app.post("/vectorstore/query")
async def vectorstore_query(request: QueryRequest):
    try:
        result = await query_vector_store(request.query, request.k)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Vector store index not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vectorstore/ingest")
async def vectorstore_ingest(file: UploadFile = File(...)):
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(status_code=400, detail="Invalid or missing filename.")
    sanitized = re.sub(r'[\s\-]+', '_', file.filename)
    sanitized = sanitized.replace('/', '_').replace('\\', '_')
    if '.' in sanitized:
        orig_name, ext = os.path.splitext(sanitized)
    else:
        orig_name, ext = sanitized, ''
    uuid_str = str(uuid.uuid4()).replace("-", "")[:8]
    max_name_len = 32 - len(ext) - len(uuid_str) - 1
    safe_name = orig_name[:max_name_len]
    unique_filename = f"{safe_name}_{uuid_str}{ext}"
    file_path = os.path.join(uploads_dir, unique_filename)
    try:
        await _save_uploaded_file_async(file, file_path)
        result = await ingest_pdf_to_vector_store(file_path)
        result["filename"] = unique_filename
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_pdf_endpoint(
    file: UploadFile = File(...),
    search_query: str = Form("Summarize this"),
    mode: str = Form("vector"),
) -> AnalysisResponse:
    await _validate_file_async(file)

    if mode not in ["vector", "multimodal"]:
        raise HTTPException(
            status_code=400,
            detail="Mode must be one of: vector, multimodal"
        )

    temp_dir = await asyncio.to_thread(tempfile.mkdtemp)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        await _save_uploaded_file_async(file, temp_file_path)

        analysis_result = await analyze_pdf(temp_file_path, search_query, mode)

        return AnalysisResponse(
            message="PDF analyzed successfully",
            mode=AnalysisMode.MULTIMODAL if mode == "multimodal" else AnalysisMode.VECTOR,
            search_query=search_query,
            filename=file.filename,
            **analysis_result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        await _cleanup_temp_files_async(temp_file_path, temp_dir)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(
        status="healthy"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        loop="asyncio"
    )
