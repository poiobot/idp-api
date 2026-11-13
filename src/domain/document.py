from __future__ import annotations

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime, timezone


class Document(BaseModel):
	model_config = ConfigDict(populate_by_name=True, json_schema_extra={"table": "Document"})
	id: Optional[str] = Field(default=None, alias="fileId")
	fileName: str = None
	uploadTimestamp: Union[datetime, str] = None
	fileType: str = None
	extractedText: Optional[str] = None
	status: str = None
	confidenceScore: Optional[float] = None
	holderId: Union[str, "PolicyHolder"] = Field(default=None, json_schema_extra={"table": "PolicyHolder"})
	policyId: Optional[Union[str, "InsurancePolicy"]] = Field(default=None, json_schema_extra={"table": "InsurancePolicy"})
	version: int = Field(default=1, alias="_version")
	created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_created")
	updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_updated")
