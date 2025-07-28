import asyncio
import base64
import os
from typing import Dict, Any, List

import aiofiles
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from ..config.llm_config import get_llm
from ..config.prompts import get_summarization_prompt
from ..schemas.llm_response_models import LLMSummaryResponse


async def _load_pdf_async(file_path: str) -> List[Document]:
    try:
        loader = PyPDFLoader(file_path)
        return await asyncio.to_thread(loader.load)
    except Exception as e:
        raise FileNotFoundError(f"Failed to load PDF: {str(e)}")


async def _split_documents_async(pages: List[Document], text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
    return await asyncio.to_thread(text_splitter.split_documents, pages)


async def _read_file_async(file_path: str) -> bytes:
    try:
        async with aiofiles.open(file_path, "rb") as pdf_file:
            return await pdf_file.read()
    except Exception as e:
        raise FileNotFoundError(f"Failed to read file: {str(e)}")


async def summarize_pdf_multimodal(file_path: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
    load_dotenv()

    if not await asyncio.to_thread(os.path.exists, file_path):
        raise FileNotFoundError("File not found")

    pdf_bytes = await _read_file_async(file_path)
    pdf_base64 = await asyncio.to_thread(base64.b64encode, pdf_bytes)
    pdf_base64_str = await asyncio.to_thread(pdf_base64.decode, "utf-8")

    system_prompt = get_summarization_prompt()

    llm = await get_llm(
        model_name="gemini-2.5-flash",
        model_provider="google_genai",
        temperature=0,
        structured_schema=LLMSummaryResponse
    )

    prompt_text = f"Please provide a {summary_type} summary of this PDF document."
    
    prompt = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt_text
            },
            {
                "type": "file",
                "source_type": "base64",
                "mime_type": "application/pdf",
                "data": pdf_base64_str,
            }
        ]
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        prompt
    ]

    try:
        structured_response = await llm.ainvoke(messages)
        return {
            "summary": structured_response.summary,
            "summary_type": structured_response.summary_type,
            "key_points": structured_response.key_points
        }
    except Exception as e:
        print(f"Multimodal summarization failed: {e}")
        return await summarize_pdf_text_based(file_path, summary_type)


async def summarize_pdf_text_based(file_path: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
    load_dotenv()

    if not await asyncio.to_thread(os.path.exists, file_path):
        raise FileNotFoundError("File not found")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000,
        length_function=len,
    )

    pages = await _load_pdf_async(file_path)
    chunks = await _split_documents_async(pages, text_splitter)

    full_content = await asyncio.to_thread(
        lambda: "\n\n".join([chunk.page_content for chunk in chunks])
    )

    system_prompt = get_summarization_prompt()

    llm = await get_llm(
        model_name="gemini-2.5-flash",
        model_provider="google_genai",
        temperature=0,
        structured_schema=LLMSummaryResponse
    )

    prompt = f"Please provide a {summary_type} summary of the following document:\n\n{full_content}"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    structured_response = await llm.ainvoke(messages)

    return {
        "summary": structured_response.summary,
        "summary_type": structured_response.summary_type,
        "key_points": structured_response.key_points
    }


async def summarize_pdf(file_path: str, summary_type: str = "comprehensive", mode: str = "vector") -> Dict[str, Any]:
    if mode == "multimodal":
        return await summarize_pdf_multimodal(file_path, summary_type)
    else:
        return await summarize_pdf_text_based(file_path, summary_type) 