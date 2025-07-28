import os
import base64
import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import SecretStr
from src.config import create_classification_prompt
from src.schemas import ClassificationResponse

load_dotenv()

app = FastAPI(
    title="PDF Document Classifier",
    description="Classify PDF documents into different document types",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class PDFDocumentClassifier:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            api_key=SecretStr(api_key),
        ).with_structured_output(ClassificationResponse)

    async def encode_pdf_to_base64(self, pdf_data: bytes) -> str | None:
        try:
            pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
            return pdf_base64
        except Exception as e:
            print(f"Error encoding PDF: {e}")
            return None

    async def classify_entire_pdf(self, pdf_data: bytes) -> ClassificationResponse:
        pdf_base64 = await self.encode_pdf_to_base64(pdf_data)

        if pdf_base64 is None:
            return ClassificationResponse(
                page_classifications=[]
            )

        pdf_part = {"type": "media",
                    "source_type": "base64",
                    "mime_type": "application/pdf",
                    "data": pdf_base64}

        classification_prompt = create_classification_prompt()
        message = []
        message.append(SystemMessage(content=classification_prompt))
        message.append(HumanMessage(content=[pdf_part]))

        try:
            response = await self.llm.ainvoke(message)
            if isinstance(response, ClassificationResponse):
                return response
            elif isinstance(response, dict):
                return ClassificationResponse(**response)
            else:
                return ClassificationResponse(page_classifications=[])
        except Exception as e:
            print(f"Error classifying PDF: {e}")
            return ClassificationResponse(
                page_classifications=[]
            )


@app.post("/classify-pdf", response_model=ClassificationResponse)
async def classify_pdf(file: UploadFile = File(...)):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        pdf_data = await file.read()
        classifier = PDFDocumentClassifier()
        result = await classifier.classify_entire_pdf(pdf_data)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
