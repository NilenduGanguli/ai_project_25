from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
from pathlib import Path
import tempfile
import json
import asyncio
import aiofiles
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import uuid
from dotenv import load_dotenv

from src.db.models import DocumentSchema, SchemaStatus, SchemaModificationRequest, SchemaModificationResponse
from src.db.connection import init_db
from src.extractors.universal import extract_with_db_schema
from src.extractors.schema_generator import generate_schema_from_documents
from src.extractors.classifier import classify_document_type
from src.config import MIN_CLASSIFICATION_CONFIDENCE, SUPPORTED_DOCUMENT_TYPES
from src.utils.schema_operations import (
    compare_schemas,
    apply_schema_modifications,
    calculate_next_version,
    generate_change_summary,
    validate_schema_modifications,
    get_modification_metadata,
    find_latest_schema_version
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Document Extraction API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.post("/extract")
async def extract_document(
    document: List[UploadFile] = File(...)
) -> JSONResponse:
    if not document or len(document) == 0:
        raise HTTPException(
            status_code=400, detail="At least one document file is required")

    for i, doc_file in enumerate(document):
        if doc_file.content_type not in SUPPORTED_DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Document {i+1} must be JPEG, PNG, or PDF. Got: {doc_file.content_type}")
        
        if not doc_file.filename or doc_file.filename.strip() == "":
            raise HTTPException(
                status_code=400, detail=f"Document {i+1} filename is invalid")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        document_paths = []

        try:
            for i, doc_file in enumerate(document):
                doc_path = temp_path / f"document_{i}_{uuid.uuid4()}"
                async with aiofiles.open(doc_path, "wb") as buffer:
                    content = await doc_file.read()
                    await buffer.write(content)
                document_paths.append(doc_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save documents: {e}")

        try:
            classification = await asyncio.wait_for(
                classify_document_type(document_paths, [doc.content_type for doc in document]),
                timeout=240.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=408,
                detail="Document classification timed out"
            )

        if not classification:
            raise HTTPException(
                status_code=400,
                detail="Unable to classify document type"
            )

        if classification.confidence < MIN_CLASSIFICATION_CONFIDENCE:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "classification_uncertain",
                    "message": "Document type classification confidence is below threshold",
                    "classification": {
                        "document_type": classification.document_type,
                        "country": classification.country,
                        "confidence": classification.confidence
                    },
                    "alternative_types": classification.alternative_types
                }
            )

        document_type = classification.document_type
        country = classification.country

        try:
            active_schema_task = DocumentSchema.find_one({
                "document_type": document_type,
                "country": country,
                "status": SchemaStatus.ACTIVE
            })

            in_review_schema_task = DocumentSchema.find_one({
                "document_type": document_type,
                "country": country,
                "status": SchemaStatus.IN_REVIEW
            })

            schema, in_review_schema = await asyncio.gather(
                active_schema_task,
                in_review_schema_task
            )

            if schema:
                extracted_data_json = await extract_with_db_schema(
                    document_paths=document_paths,
                    document_types=[doc.content_type for doc in document],
                    document_schema=schema
                )

                extracted_data = json.loads(extracted_data_json)

                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "extracted",
                        "data": extracted_data,
                        "classification": {
                            "document_type": classification.document_type,
                            "country": classification.country,
                            "confidence": classification.confidence
                        },
                        "schema_used": {
                            "document_type": schema.document_type,
                            "country": schema.country,
                            "version": schema.version
                        }
                    }
                )

            if in_review_schema:
                return JSONResponse(
                    status_code=202,
                    content={
                        "status": "pending_review",
                        "message": "A schema for this document type is already awaiting approval.",
                        "classification": {
                            "document_type": classification.document_type,
                            "country": classification.country,
                            "confidence": classification.confidence
                        },
                        "schema_id": str(in_review_schema.id),
                        "document_type": in_review_schema.document_type,
                        "country": in_review_schema.country
                    }
                )

            generated_schema = await generate_schema_from_documents(
                document_paths=document_paths,
                document_types=[doc.content_type for doc in document],
                document_type=document_type,
                country=country
            )

            if not generated_schema:
                raise HTTPException(
                    status_code=500, detail="Failed to generate schema")

            schema_dict = {}
            for field_name, field_def in generated_schema.document_schema.items():
                if isinstance(field_def, dict):
                    schema_dict[field_name] = field_def
                else:
                    schema_dict[field_name] = {
                        "type": getattr(field_def, 'type', 'string'),
                        "description": getattr(field_def, 'description', ''),
                        "required": getattr(field_def, 'required', True),
                        "example": getattr(field_def, 'example', None)
                    }

            new_schema = DocumentSchema(
                document_type=document_type,
                country=country,
                document_schema=schema_dict,
                status=SchemaStatus.IN_REVIEW,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            await new_schema.insert()

            return JSONResponse(
                status_code=201,
                content={
                    "status": "schema_generated",
                    "message": "Schema generated and saved for review Extraction not performed.",
                    "classification": {
                        "document_type": classification.document_type,
                        "country": classification.country,
                        "confidence": classification.confidence
                    },
                    "generated_schema": {
                        "document_type": generated_schema.document_type,
                        "country": generated_schema.country,
                        "confidence": generated_schema.confidence,
                        "schema": schema_dict
                    },
                    "schema_id": str(new_schema.id)
                }
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Extraction failed, {e}")


@app.get("/schemas")
async def get_all_schemas() -> JSONResponse:
    try:
        schemas = await DocumentSchema.find_all().to_list()

        schema_list = []
        for schema in schemas:
            schema_list.append({
                "id": str(schema.id),
                "document_type": schema.document_type,
                "country": schema.country,
                "status": schema.status,
                "version": schema.version,
                "created_at": schema.created_at.isoformat(),
                "updated_at": schema.updated_at.isoformat(),
                "schema": schema.document_schema
            })

        return JSONResponse(
            status_code=200,
            content={
                "schemas": schema_list,
                "total_count": len(schema_list)
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve schemas: {e}")


@app.put("/schemas/{schema_id}/approve")
async def approve_schema(schema_id: str) -> JSONResponse:
    try:
        schema = await DocumentSchema.get(schema_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found")

        if schema.status != SchemaStatus.IN_REVIEW:
            raise HTTPException(
                status_code=400,
                detail="Schema must be in IN_REVIEW status to approve"
            )

        existing_active = await DocumentSchema.find_one({
            "document_type": schema.document_type,
            "country": schema.country,
            "status": SchemaStatus.ACTIVE
        })

        deprecated_schema_info = None
        if existing_active:
            existing_active.status = SchemaStatus.DEPRECATED
            existing_active.updated_at = datetime.now(timezone.utc)
            await existing_active.save()
            deprecated_schema_info = {
                "id": str(existing_active.id),
                "version": existing_active.version
            }

        schema.status = SchemaStatus.ACTIVE
        schema.updated_at = datetime.now(timezone.utc)
        if existing_active:
            schema.version = existing_active.version + 1

        await schema.save()

        return JSONResponse(
            status_code=200,
            content={
                "message": "Schema approved successfully",
                "schema": {
                    "id": str(schema.id),
                    "document_type": schema.document_type,
                    "country": schema.country,
                    "status": schema.status,
                    "version": schema.version,
                    "updated_at": schema.updated_at.isoformat()
                },
                "deprecated_schema": deprecated_schema_info
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve schema: {e}")


@app.put("/schemas/{schema_id}/modify")
async def modify_schema(schema_id: str, request: SchemaModificationRequest) -> JSONResponse:
    try:
        schema = await DocumentSchema.get(schema_id)
        if not schema:
            raise HTTPException(status_code=404, detail="Schema not found")

        latest_schema = await find_latest_schema_version(schema.document_type, schema.country)
        if not latest_schema or latest_schema.id != schema.id:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot modify schema version, only the latest version can be modified. Latest schema ID: {str(latest_schema.id) if latest_schema else 'unknown'}"
            )

        is_valid, error_message = validate_schema_modifications(request.modifications)
        if not is_valid:
            raise HTTPException(
                status_code=400, detail=f"Invalid modifications: {error_message}")

        original_schema = schema.document_schema.copy()
        modified_schema = apply_schema_modifications(
            original_schema, request.modifications)

        changes = compare_schemas(original_schema, modified_schema)

        if not changes:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No changes detected in the provided modifications",
                    "schema_id": schema_id,
                    "current_version": schema.version,
                    "original_schema": original_schema
                }
            )

        next_version = await calculate_next_version(schema)

        change_summary = generate_change_summary(changes)
        modification_metadata = get_modification_metadata(
            changes, request.change_description)

        schema.status = SchemaStatus.DEPRECATED
        schema.updated_at = datetime.now(timezone.utc)
        await schema.save()

        new_schema = DocumentSchema(
            document_type=schema.document_type,
            country=schema.country,
            document_schema=modified_schema,
            status=SchemaStatus.IN_REVIEW,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=next_version
        )

        await new_schema.insert()

        response = SchemaModificationResponse(
            schema_id=str(new_schema.id),
            current_version=schema.version,
            proposed_version=next_version,
            changes=[change.model_dump() for change in changes],
            original_schema=original_schema,
            modified_schema=modified_schema,
            change_summary=change_summary,
            modification_metadata=modification_metadata
        )

        return JSONResponse(
            status_code=201,
            content={
                "status": "schema_modified",
                "message": "Schema successfully modified and saved",
                "original_schema_info": {
                    "id": str(schema.id),
                    "version": schema.version,
                    "status": schema.status
                },
                "new_schema_info": {
                    "id": str(new_schema.id),
                    "document_type": new_schema.document_type,
                    "country": new_schema.country,
                    "status": new_schema.status,
                    "version": new_schema.version,
                    "created_at": new_schema.created_at.isoformat(),
                    "updated_at": new_schema.updated_at.isoformat()
                },
                "modification_details": response.model_dump(),
                "note": "Changes have been saved to the database"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to apply schema modification: {e}")


@app.get("/")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8005))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,
        loop="asyncio",
        access_log=False,
        log_level="info"
    )
