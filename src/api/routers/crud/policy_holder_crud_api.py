from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.policy_holder_crud_ctl import PolicyHolderCrudCTL
from domain.policy_holder import PolicyHolder

disable_installed_extensions_check()

router = APIRouter()
handler = PolicyHolderCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ()
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: none"


@router.post(path="/idp/policy_holder", response_model=PolicyHolder, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_policy_holder(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		policy_holder = PolicyHolder(**data)
		policy_holder = handler.create(policy_holder)
		return policy_holder
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"policy_holder: {data} already exists")


@router.get(path="/idp/policy_holder", response_model=LimitOffsetPage[PolicyHolder], response_model_by_alias=False)
async def fetch_policy_holder(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, PolicyHolder)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	policy_holder = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(policy_holder))
	return create_page(policy_holder, total=handler.count(query=query), params=page)


@router.get(path="/idp/policy_holder/{id}", tags=["policy_holder"], response_model=PolicyHolder, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_policy_holder(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	policy_holder = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if policy_holder is None:
		raise HTTPException(status_code=404, detail=f"policy_holder {id} not found")
	return policy_holder


@router.put(path="/idp/policy_holder/{id}", tags=["policy_holder"], status_code=status.HTTP_200_OK)
async def update_policy_holder(id: str, data: Dict = Body):
	policy_holder = handler.get_by_id(id)
	if policy_holder is None:
		raise HTTPException(status_code=404, detail=f"policy_holder {id} not found")
	merged = policy_holder
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, PolicyHolder(**merged)):
		return JSONResponse(content={"policy_holder": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/policy_holder/{id}", tags=["policy_holder"], status_code=status.HTTP_202_ACCEPTED)
async def delete_policy_holder(id: str):
	if handler.delete(id):
		return JSONResponse(content={"policy_holder": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"policy_holder: {id} not found")


add_pagination(router)
