from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.insurance_policy_crud_ctl import InsurancePolicyCrudCTL
from domain.insurance_policy import InsurancePolicy

disable_installed_extensions_check()

router = APIRouter()
handler = InsurancePolicyCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ("holderId",)
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: holderId"


@router.post(path="/idp/insurance_policy", response_model=InsurancePolicy, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_insurance_policy(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		insurance_policy = InsurancePolicy(**data)
		insurance_policy = handler.create(insurance_policy)
		return insurance_policy
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"insurance_policy: {data} already exists")


@router.get(path="/idp/insurance_policy", response_model=LimitOffsetPage[InsurancePolicy], response_model_by_alias=False)
async def fetch_insurance_policy(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, InsurancePolicy)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	insurance_policy = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(insurance_policy))
	return create_page(insurance_policy, total=handler.count(query=query), params=page)


@router.get(path="/idp/insurance_policy/{id}", tags=["insurance_policy"], response_model=InsurancePolicy, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_insurance_policy(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	insurance_policy = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if insurance_policy is None:
		raise HTTPException(status_code=404, detail=f"insurance_policy {id} not found")
	return insurance_policy


@router.put(path="/idp/insurance_policy/{id}", tags=["insurance_policy"], status_code=status.HTTP_200_OK)
async def update_insurance_policy(id: str, data: Dict = Body):
	insurance_policy = handler.get_by_id(id)
	if insurance_policy is None:
		raise HTTPException(status_code=404, detail=f"insurance_policy {id} not found")
	merged = insurance_policy
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, InsurancePolicy(**merged)):
		return JSONResponse(content={"insurance_policy": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/insurance_policy/{id}", tags=["insurance_policy"], status_code=status.HTTP_202_ACCEPTED)
async def delete_insurance_policy(id: str):
	if handler.delete(id):
		return JSONResponse(content={"insurance_policy": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"insurance_policy: {id} not found")


add_pagination(router)
