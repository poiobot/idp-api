from __future__ import annotations

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime, timezone


class PolicyHolder(BaseModel):
	model_config = ConfigDict(populate_by_name=True, json_schema_extra={"table": "PolicyHolder"})
	id: Optional[str] = Field(default=None, alias="holderId")
	firstName: str = None
	lastName: str = None
	email: str = None
	phoneNumber: str = None
	privacyPreferences: Optional[str] = None
	version: int = Field(default=1, alias="_version")
	created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_created")
	updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_updated")
