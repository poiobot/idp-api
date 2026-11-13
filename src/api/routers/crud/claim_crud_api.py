from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.claim_crud_ctl import ClaimCrudCTL
from domain.claim import Claim

disable_installed_extensions_check()

router = APIRouter()
handler = ClaimCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ("holderId", "policyId",)
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: holderId, policyId"


@router.post(path="/idp/claim", response_model=Claim, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_claim(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		claim = Claim(**data)
		claim = handler.create(claim)
		return claim
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"claim: {data} already exists")


@router.get(path="/idp/claim", response_model=LimitOffsetPage[Claim], response_model_by_alias=False)
async def fetch_claim(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, Claim)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	claim = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(claim))
	return create_page(claim, total=handler.count(query=query), params=page)


@router.get(path="/idp/claim/{id}", tags=["claim"], response_model=Claim, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_claim(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	claim = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if claim is None:
		raise HTTPException(status_code=404, detail=f"claim {id} not found")
	return claim


@router.put(path="/idp/claim/{id}", tags=["claim"], status_code=status.HTTP_200_OK)
async def update_claim(id: str, data: Dict = Body):
	claim = handler.get_by_id(id)
	if claim is None:
		raise HTTPException(status_code=404, detail=f"claim {id} not found")
	merged = claim
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, Claim(**merged)):
		return JSONResponse(content={"claim": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/claim/{id}", tags=["claim"], status_code=status.HTTP_202_ACCEPTED)
async def delete_claim(id: str):
	if handler.delete(id):
		return JSONResponse(content={"claim": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"claim: {id} not found")


add_pagination(router)
