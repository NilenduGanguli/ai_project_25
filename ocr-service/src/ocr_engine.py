import os
import base64
import asyncio
from typing import Dict, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

load_dotenv()


class OCRExtractionResponse(BaseModel):
    """Structured response for OCR text extraction"""
    extracted_text: str = Field(
        description="All text extracted from the image or document, preserving structure and formatting"
    )
    confidence_score: float = Field(
        description="Confidence score between 0.0 and 1.0 indicating extraction quality",
        ge=0.0,
        le=1.0
    )
    notes: Optional[str] = Field(
        default=None,
        description="Any notes about text quality, illegibility, or extraction challenges"
    )


def get_ocr_llm() -> ChatGoogleGenerativeAI:
    """Initialize the LLM for OCR without structured output"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.0,
        google_api_key=api_key,
    )


def create_ocr_prompt() -> str:
    """Create the system prompt for OCR extraction"""
    return """You are an expert OCR (Optical Character Recognition) system with exceptional text extraction capabilities.

Your task is to extract ALL visible text from the provided image or document with the highest accuracy possible.

EXTRACTION GUIDELINES:
1. Extract EVERY piece of text visible in the image/document
2. Preserve the original structure, layout, and formatting as much as possible
3. Maintain proper spacing, line breaks, and paragraph structure
4. Include headers, footers, page numbers, watermarks, and any other text
5. For tables, preserve row/column structure using spacing or delimiters
6. Extract text in reading order (left-to-right, top-to-bottom for English)
7. Do not modify, correct, or interpret the text - extract exactly as shown
8. Include special characters, symbols, and punctuation marks
9. For multi-language documents, extract text in all languages present

IMPORTANT: Simply output the extracted text directly. Do not include any preamble, explanation, or metadata. Just the extracted text."""


async def extract_text_from_image(
    image_data: bytes,
    content_type: str = "image/png"
) -> Dict[str, any]:
    """
    Extract text from an image using Google Gemini Vision
    
    Args:
        image_data: Raw image bytes
        content_type: MIME type of the image
        
    Returns:
        Dict containing extracted text and confidence score
    """
    # Encode image to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    
    # Get LLM
    llm = get_ocr_llm()
    
    # Create messages
    system_prompt = create_ocr_prompt()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract all text from this image with maximum accuracy."
                },
                {
                    "type": "image_url",
                    "image_url": f"data:{content_type};base64,{image_base64}"
                }
            ]
        )
    ]
    
    # Extract text
    try:
        response = await asyncio.to_thread(llm.invoke, messages)
        
        # Extract text from response
        extracted_text = response.content if hasattr(response, 'content') else str(response)
        
        # Calculate confidence based on text length and quality
        confidence = 0.9 if len(extracted_text.strip()) > 10 else 0.5
        
        return {
            "text": extracted_text,
            "confidence": confidence,
            "notes": ""
        }
        
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")


async def extract_text_from_pdf(
    pdf_data: bytes
) -> Dict[str, any]:
    """
    Extract text from a PDF using Google Gemini Vision
    
    Args:
        pdf_data: Raw PDF bytes
        
    Returns:
        Dict containing extracted text and confidence score
    """
    # Encode PDF to base64
    pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
    
    # Get LLM
    llm = get_ocr_llm()
    
    # Create messages
    system_prompt = create_ocr_prompt()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract all text from this PDF document with maximum accuracy. Process all pages."
                },
                {
                    "type": "media",
                    "mime_type": "application/pdf",
                    "data": pdf_base64
                }
            ]
        )
    ]
    
    # Extract text
    try:
        response = await asyncio.to_thread(llm.invoke, messages)
        
        # Extract text from response
        extracted_text = response.content if hasattr(response, 'content') else str(response)
        
        # Calculate confidence based on text length and quality
        confidence = 0.9 if len(extracted_text.strip()) > 10 else 0.5
        
        return {
            "text": extracted_text,
            "confidence": confidence,
            "notes": ""
        }
        
    except Exception as e:
        raise Exception(f"PDF OCR extraction failed: {str(e)}")
