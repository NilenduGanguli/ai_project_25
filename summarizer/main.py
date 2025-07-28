import asyncio
import os
import tempfile

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas.response_models import SummaryResponse, HealthResponse, AnalysisMode
from src.utils.summarizer import summarize_pdf
from src.utils.utils import _validate_file_async, _save_uploaded_file_async, _cleanup_temp_files_async

load_dotenv()

app = FastAPI(
    title="PDF Summarizer API",
    description="Summarize PDF files efficiently",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_pdf_endpoint(
    file: UploadFile = File(...),
    summary_type: str = Form("comprehensive"),
    mode: str = Form("vector"),
) -> SummaryResponse:
    await _validate_file_async(file)

    if mode not in ["vector", "multimodal"]:
        raise HTTPException(
            status_code=400,
            detail="Mode must be one of: vector, multimodal"
        )
        
    if summary_type not in ["comprehensive", "brief", "detailed"]:
        raise HTTPException(
            status_code=400,
            detail="Summary type must be one of: comprehensive, brief, detailed"
        )

    temp_dir = await asyncio.to_thread(tempfile.mkdtemp)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        await _save_uploaded_file_async(file, temp_file_path)

        summary_result = await summarize_pdf(temp_file_path, summary_type, mode)
        
        summary_data = {k: v for k, v in summary_result.items() if k != 'summary_type'}

        return SummaryResponse(
            message="PDF summarized successfully",
            mode=AnalysisMode.MULTIMODAL if mode == "multimodal" else AnalysisMode.VECTOR,
            summary_type=summary_type,
            filename=file.filename,
            **summary_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
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
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        loop="asyncio"
    )
