from __future__ import annotations

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime, timezone


class Claim(BaseModel):
	model_config = ConfigDict(populate_by_name=True, json_schema_extra={"table": "Claim"})
	id: Optional[str] = Field(default=None, alias="claimId")
	claimNumber: str = None
	holderId: Union[str, "PolicyHolder"] = Field(default=None, json_schema_extra={"table": "PolicyHolder"})
	policyId: Union[str, "InsurancePolicy"] = Field(default=None, json_schema_extra={"table": "InsurancePolicy"})
	claimDate: date = None
	claimStatus: str = None
	claimAmount: float = 0.0
	description: Optional[str] = None
	version: int = Field(default=1, alias="_version")
	created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_created")
	updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="_updated")
