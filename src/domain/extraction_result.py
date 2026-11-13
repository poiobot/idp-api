from __future__ import annotations

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime, timezone


class ExtractionResult(BaseModel):
	model_config = ConfigDict(populate_by_name=True, json_schema_extra={"table": "ExtractionResult"})
	id: Optional[str] = Field(default=None, alias="resultId")
	fileId: Union[str, "Document"] = Field(default=None, json_schema_extra={"table": "Document"})
	classificationId: Union[str, "DocumentClassification"] = Field(default=None, json_schema_extra={"table": "DocumentClassification"})
	structuredData: str = None
	fieldConfidenceScores: Optional[str] = None
	auditTrail: Optional[str] = None
	version: int = Field(default=1, alias="_version")
	created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_created")
	updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_updated")
