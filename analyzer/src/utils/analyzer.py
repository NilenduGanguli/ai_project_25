import asyncio
import base64
import os
from typing import List, Dict, Any

import aiofiles
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from pdf2image import convert_from_path
import requests
import tempfile
from ..config.llm_config import get_llm
from ..config.prompts import get_multimodal_prompt, get_text_analysis_prompt
from ..schemas.llm_response_models import LLMResponse


async def _create_embeddings_async() -> GoogleGenerativeAIEmbeddings:
    return await asyncio.to_thread(
        lambda: GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    )


# Replace with Azure OCR
# def extract_text_from_image(image):
    # return "test"
    # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    #     image.save(tmp.name)
    #     tmp_path = tmp.name
    # with open(tmp_path, "rb") as f:
    #     files = {"file": f}
    #     response = requests.post("http://localhost:8006/extract-text", files=files)
    #     print("Extracted Text:",response.json())
    #     if response.status_code == 200:
    #         return response.json()["text"]
    #     else:
    #         print(f"Error: {response.status_code} - {response.text}")
    #         return ""


async def _load_pdf_async(file_path: str) -> List[Document]:
    try:
        loader = PyPDFLoader(file_path)
        docs = await asyncio.to_thread(loader.load)
        if all(not doc.page_content.strip() for doc in docs):
            images = await asyncio.to_thread(convert_from_path, file_path)
            ocr_docs = []
            for i, img in enumerate(images):
                text = await asyncio.to_thread(extract_text_from_image, img)
                meta = docs[i].metadata if i < len(docs) else {"page": i}
                ocr_docs.append(Document(page_content=text, metadata=meta))
            return ocr_docs

        for i, doc in enumerate(docs):
            if not doc.page_content.strip():
                images = await asyncio.to_thread(convert_from_path, file_path, first_page=i+1, last_page=i+1)
                if images:
                    text = await asyncio.to_thread(extract_text_from_image, images[0])
                    docs[i].page_content = text
        return docs
    except Exception as e:
        raise FileNotFoundError(f"Failed to load PDF: {str(e)}")


async def _split_documents_async(pages: List[Document], text_splitter: RecursiveCharacterTextSplitter, file_path: str = None) -> List[Document]:
    chunks = await asyncio.to_thread(text_splitter.split_documents, pages)
    if file_path:
        for chunk in chunks:
            chunk.metadata["source_path"] = file_path
    return chunks


async def _create_vector_store_async(chunks: List[Document], embeddings: GoogleGenerativeAIEmbeddings, index_path: str = "faiss_index") -> FAISS:
    if os.path.exists(index_path):
        return await asyncio.to_thread(FAISS.load_local, index_path, embeddings, allow_dangerous_deserialization=True)
    store = await asyncio.to_thread(FAISS.from_documents, chunks, embeddings)
    await asyncio.to_thread(store.save_local, index_path)
    return store


async def _similarity_search_async(vector_store: FAISS, search_query: str, k: int = 4) -> List[Document]:
    return await asyncio.to_thread(vector_store.similarity_search, search_query, k)


async def _read_file_async(file_path: str) -> bytes:
    try:
        async with aiofiles.open(file_path, "rb") as pdf_file:
            return await pdf_file.read()
    except Exception as e:
        raise FileNotFoundError(f"Failed to read file: {str(e)}")


def _format_retrieved_vectors(docs: List[Document]) -> List[Dict[str, Any]]:
    return [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata,
            "source_path": doc.metadata.get("source_path")
        }
        for doc in docs
    ]


async def analyze_pdf_multimodal(file_path: str, search_query: str = "Analyze this PDF document") -> Dict[str, Any]:
    load_dotenv()

    if not await asyncio.to_thread(os.path.exists, file_path):
        raise FileNotFoundError("File not found")

    pdf_bytes = await _read_file_async(file_path)
    pdf_base64 = await asyncio.to_thread(base64.b64encode, pdf_bytes)
    pdf_base64_str = await asyncio.to_thread(pdf_base64.decode, "utf-8")

    system_prompt = get_multimodal_prompt()

    llm = await get_llm(
        model_name="gemini-2.5-flash",
        model_provider="google_genai",
        temperature=0,
        structured_schema=LLMResponse
    )

    prompt = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"Please analyze this PDF document and respond to: {search_query}"
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
            "response": structured_response.response,
            "analysis_type": "multimodal",
            "retrieved_vectors": []
        }
    except Exception as e:
        print(f"Multimodal analysis failed: {e}")
        return await analyze_pdf_text_based(file_path, search_query)


async def analyze_pdf_text_based(file_path: str, search_query: str = "Summarize this") -> Dict[str, Any]:
    load_dotenv()

    if not await asyncio.to_thread(os.path.exists, file_path):
        raise FileNotFoundError("File not found")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000,
        length_function=len,
    )

    pages_task = _load_pdf_async(file_path)
    embeddings_task = _create_embeddings_async()
    
    pages, embeddings = await asyncio.gather(pages_task, embeddings_task)

    chunks = await _split_documents_async(pages, text_splitter, file_path)

    vector_store = await asyncio.to_thread(FAISS.from_documents, chunks, embeddings)

    system_prompt = get_text_analysis_prompt()

    llm_task = get_llm(
        model_name="gemini-2.5-flash",
        model_provider="google_genai",
        temperature=0,
        structured_schema=LLMResponse
    )
    search_task = _similarity_search_async(vector_store, search_query, k=4)
    
    llm, docs = await asyncio.gather(llm_task, search_task)

    if not docs:
        return {
            "response": "No relevant content found in the document.",
            "retrieved_vectors": [],
            "analysis_type": "vector"
        }

    target_content = await asyncio.to_thread(
        lambda: "\n---\n".join([doc.page_content for doc in docs])
    )
    prompt = f"Based on the following text, {search_query}:\n\n{target_content}"
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    structured_response = await llm.ainvoke(messages)

    return {
        "response": structured_response.response,
        "retrieved_vectors": _format_retrieved_vectors(docs),
        "analysis_type": "vector",
    }


async def analyze_pdf(file_path: str = "demo.pdf", search_query: str = "Summarize this", mode: str = "vector") -> Dict[str, Any]:
    if mode == "multimodal":
        return await analyze_pdf_multimodal(file_path, search_query)
    elif mode == "vector":
        return await analyze_pdf_text_based(file_path, search_query)
    else:
        return await analyze_pdf_text_based(file_path, search_query)

async def query_vector_store(search_query: str, k: int = 4, index_path: str = "faiss_index") -> dict:
    if not os.path.exists(index_path):
        raise FileNotFoundError("Vector store index not found.")
    embeddings = await _create_embeddings_async()
    vector_store = await asyncio.to_thread(FAISS.load_local, index_path, embeddings, allow_dangerous_deserialization=True)
    docs = await _similarity_search_async(vector_store, search_query, k)
    return {
        "results": _format_retrieved_vectors(docs)
    }

async def ingest_pdf_to_vector_store(file_path: str, index_path: str = "faiss_index") -> dict:
    os.makedirs(index_path, exist_ok=True)
    pages = await _load_pdf_async(file_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000,
        length_function=len,
    )
    chunks = await _split_documents_async(pages, text_splitter, file_path)
    embeddings = await _create_embeddings_async()
    index_file = os.path.join(index_path, "index.faiss")
    if os.path.exists(index_file):
        vector_store = await asyncio.to_thread(FAISS.load_local, index_path, embeddings, allow_dangerous_deserialization=True)
        await asyncio.to_thread(vector_store.add_documents, chunks)
    else:
        vector_store = await asyncio.to_thread(FAISS.from_documents, chunks, embeddings)
    await asyncio.to_thread(vector_store.save_local, index_path)
    return {"message": "PDF ingested and index updated."}
