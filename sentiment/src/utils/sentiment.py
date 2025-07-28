import base64
import asyncio
from pathlib import Path
from typing import Optional, List

import aiofiles
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from src.config.llm_config import get_llm

from src.config.prompts import get_multimodal_sentiment_prompt, get_text_sentiment_prompt
from src.schemas.llm_response_models import LLMSentimentResponse


async def load_pdf_async(pdf_path: str) -> List[Document]:
    def _load_pdf():
        loader = PyPDFLoader(pdf_path)
        return loader.load()

    return await asyncio.to_thread(_load_pdf)


async def analyze_text_sentiment(text: str) -> Optional[dict]:
    base_prompt = get_text_sentiment_prompt()

    prompt = f"{base_prompt}\n\nText to analyze:\n{text}"

    structured_llm = await get_llm(
        model_name="gemini-2.5-flash",
        model_provider="google_genai",
        temperature=0,
        structured_schema=LLMSentimentResponse,
    )

    try:
        response = await structured_llm.ainvoke(prompt)
        return {
            "sentiment": response.sentiment,
            "score": response.score,
            "summary": response.summary
        }
    except Exception as e:
        print(f"Text sentiment analysis error: {e}")
        return None


async def analyze_pdf_sentiment_multimodal(pdf_path: Path) -> Optional[dict]:
    if not await asyncio.to_thread(pdf_path.exists):
        print(f"PDF file not found: {pdf_path}")
        return None

    load_dotenv()

    try:
        async with aiofiles.open(pdf_path, "rb") as pdf_file:
            pdf_bytes = await pdf_file.read()
            pdf_base64 = await asyncio.to_thread(base64.b64encode, pdf_bytes)
            pdf_base64_str = await asyncio.to_thread(pdf_base64.decode, "utf-8")

        system_prompt = get_multimodal_sentiment_prompt()
        user_prompt = """Analyze the sentiment of this PDF document."""

        llm = await get_llm(
            model_name="gemini-2.5-flash",
            model_provider="google_genai",
            temperature=0,
            structured_schema=LLMSentimentResponse,
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "file",
                        "source_type": "base64",
                        "mime_type": "application/pdf",
                        "data": pdf_base64_str,
                    },
                ]
            ),
        ]

        response = await llm.ainvoke(messages)
        return {
            "sentiment": response.sentiment,
            "score": response.score,
            "summary": response.summary
        }

    except Exception as e:
        print(f"Multimodal sentiment analysis error: {e}")
        return None


async def analyze_pdf_sentiment_text_based(pdf_path: Path) -> Optional[dict]:
    try:
        pages = await load_pdf_async(str(pdf_path))
        full_text = "\n".join([page.page_content for page in pages])

        if not full_text.strip():
            return {
                "sentiment": "neutral",
                "score": 0.1,
                "summary": "No text could be extracted from the PDF."
            }

        result = await analyze_text_sentiment(full_text)

        if result:
            return result
        else:
            return {
                "sentiment": "neutral",
                "score": 0.1,
                "summary": "Text-based sentiment analysis failed."
            }

    except Exception as e:
        print(f"Text-based PDF sentiment analysis error: {e}")
        return {
            "sentiment": "neutral",
            "score": 0.1,
            "summary": f"Text-based analysis error: {str(e)}"
        }
