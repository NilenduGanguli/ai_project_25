from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from beanie import Document
from pydantic import BaseModel, Field
from enum import Enum


class SchemaStatus(str, Enum):
    ACTIVE = "active"
    IN_REVIEW = "in_review"
    DEPRECATED = "deprecated"


class DocumentTypeClassification(BaseModel):
    document_type: str = Field(..., description="Classified document type")
    confidence: float = Field(..., ge=0, le=1,
                              description="Classification confidence")
    country: str = Field(...,
                         description="Country of document issuance (ISO 3166-1 alpha-2 code)")
    alternative_types: List[Dict[str, float]] = Field(
        default_factory=list, description="Alternative document types with confidence scores")


class FieldModification(BaseModel):
    field_name: str = Field(...,
                            description="Name of the field being modified")
    action: str = Field(..., description="Action: 'add', 'update', 'remove'")
    old_definition: Optional[Dict[str, Any]] = Field(
        default=None, description="Previous field definition (for update/remove)")
    new_definition: Optional[Dict[str, Any]] = Field(
        default=None, description="New field definition (for add/update)")


class SchemaModificationRequest(BaseModel):
    modifications: Dict[str, Optional[Dict[str, Any]]] = Field(
        ..., description="Field modifications to apply to the schema (use null to remove fields)")
    change_description: Optional[str] = Field(
        default=None, description="Description of the changes being made")


class SchemaChange(BaseModel):
    change_type: str = Field(
        ..., description="Type of change: 'field_added', 'field_updated', 'field_removed'")
    field_name: str = Field(..., description="Name of the field that changed")
    old_value: Optional[Dict[str, Any]] = Field(
        default=None, description="Previous value (for updates/removals)")
    new_value: Optional[Dict[str, Any]] = Field(
        default=None, description="New value (for additions/updates)")


class SchemaModificationResponse(BaseModel):
    schema_id: str = Field(..., description="ID of the schema being modified")
    current_version: int = Field(...,
                                 description="Current version of the schema")
    proposed_version: int = Field(...,
                                  description="Proposed new version number")
    changes: List[SchemaChange] = Field(...,
                                        description="List of changes detected")
    original_schema: Dict[str,
                          Any] = Field(..., description="Original schema definition")
    modified_schema: Dict[str, Any] = Field(
        ..., description="Schema after applying modifications")
    change_summary: str = Field(..., description="Summary of changes made")
    modification_metadata: Dict[str, Any] = Field(
        ..., description="Metadata about the modification")


class DocumentSchema(Document):
    document_type: str = Field(...,
                               description="Type of document (e.g., pan_card, passport)")
    country: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    document_schema: Dict[str, Any] = Field(
        ..., description="JSON schema definition with field types and descriptions")
    status: SchemaStatus = Field(
        default=SchemaStatus.IN_REVIEW, description="Schema approval status")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, description="Schema version number")

    class Settings:
        name = "document_schemas"
        indexes = [
            [("document_type", 1), ("country", 1)],
        ]
