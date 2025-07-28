import asyncio
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.schemas.response_models import (
    SentimentAnalysisResponse,
    SentimentResult,
    HealthResponse,
)
from src.utils.sentiment import (
    analyze_pdf_sentiment_multimodal,
    analyze_pdf_sentiment_text_based
)
from src.utils.utils import _validate_file_async, _save_uploaded_file_async, _cleanup_temp_files_async

load_dotenv()

app = FastAPI(
    title="Sentiment Analysis API",
    description="Analyze sentiment of text and PDF documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sentiment-pdf", response_model=SentimentAnalysisResponse)
async def analyze_pdf_sentiment_endpoint(
    file: UploadFile = File(...),
    mode: str = Form("multimodal", pattern=r"^(vector|multimodal)$")
) -> SentimentAnalysisResponse:

    await _validate_file_async(file)

    temp_dir = await asyncio.to_thread(tempfile.mkdtemp)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        await _save_uploaded_file_async(file, temp_file_path)
        pdf_path = Path(temp_file_path)

        if mode == "multimodal":
            result = await analyze_pdf_sentiment_multimodal(pdf_path)
        elif mode == "vector":
            result = await analyze_pdf_sentiment_text_based(pdf_path)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid mode. Must be 'vector' or 'multimodal'."
            )

        if not result:
            raise HTTPException(
                status_code=500,
                detail="Sentiment analysis failed"
            )

        sentiment_result = SentimentResult(**result)

        return SentimentAnalysisResponse(
            message="PDF sentiment analyzed successfully",
            mode=mode,
            filename=file.filename,
            result=sentiment_result,
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
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        loop="asyncio"
    )
