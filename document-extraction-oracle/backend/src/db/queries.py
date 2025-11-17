"""
Database query helpers for Oracle synchronous operations
"""
from sqlalchemy import select, and_
from src.db.models import DocumentSchema, SchemaStatus
from src.db.connection import db
from src.db.sync_wrapper import run_in_threadpool
from datetime import datetime, timezone
from typing import Optional, List
import uuid


def _get_schema_sync(document_type: str, country: str, status: SchemaStatus) -> Optional[DocumentSchema]:
    """Get a schema synchronously"""
    session = db.session_factory()
    try:
        stmt = select(DocumentSchema).where(
            and_(
                DocumentSchema.document_type == document_type,
                DocumentSchema.country == country,
                DocumentSchema.status == status
            )
        )
        result = session.execute(stmt)
        return result.scalar_one_or_none()
    finally:
        session.close()


@run_in_threadpool
async def get_schema(document_type: str, country: str, status: SchemaStatus) -> Optional[DocumentSchema]:
    return _get_schema_sync(document_type, country, status)


def _get_all_schemas_sync() -> List[DocumentSchema]:
    """Get all schemas synchronously"""
    session = db.session_factory()
    try:
        stmt = select(DocumentSchema)
        result = session.execute(stmt)
        return list(result.scalars().all())
    finally:
        session.close()


@run_in_threadpool
async def get_all_schemas() -> List[DocumentSchema]:
    return _get_all_schemas_sync()


def _get_schema_by_id_sync(schema_id: uuid.UUID) -> Optional[DocumentSchema]:
    """Get schema by ID synchronously"""
    session = db.session_factory()
    try:
        # Convert UUID to bytes for Oracle RAW(16) comparison
        schema_id_bytes = schema_id.bytes if isinstance(schema_id, uuid.UUID) else uuid.UUID(schema_id).bytes
        stmt = select(DocumentSchema).where(DocumentSchema.id == schema_id_bytes)
        result = session.execute(stmt)
        return result.scalar_one_or_none()
    finally:
        session.close()


@run_in_threadpool
async def get_schema_by_id(schema_id: uuid.UUID) -> Optional[DocumentSchema]:
    return _get_schema_by_id_sync(schema_id)


def _save_schema_sync(schema: DocumentSchema) -> bytes:
    """Save a new schema synchronously"""
    session = db.session_factory()
    try:
        session.add(schema)
        session.commit()
        session.refresh(schema)
        return schema.id
    finally:
        session.close()


@run_in_threadpool
async def save_schema(schema: DocumentSchema) -> bytes:
    return _save_schema_sync(schema)


def _update_schema_sync(schema: DocumentSchema):
    """Update an existing schema synchronously"""
    session = db.session_factory()
    try:
        session.merge(schema)
        session.commit()
    finally:
        session.close()


@run_in_threadpool
async def update_schema(schema: DocumentSchema):
    return _update_schema_sync(schema)


def _delete_schema_sync(schema: DocumentSchema):
    """Delete a schema synchronously"""
    session = db.session_factory()
    try:
        # Re-attach to session if detached
        if schema not in session:
            schema = session.merge(schema)
        session.delete(schema)
        session.commit()
    finally:
        session.close()


@run_in_threadpool
async def delete_schema(schema: DocumentSchema):
    return _delete_schema_sync(schema)
