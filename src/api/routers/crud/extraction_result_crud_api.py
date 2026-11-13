from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.extraction_result_crud_ctl import ExtractionResultCrudCTL
from domain.extraction_result import ExtractionResult

disable_installed_extensions_check()

router = APIRouter()
handler = ExtractionResultCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ("fileId", "classificationId",)
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: fileId, classificationId"


@router.post(path="/idp/extraction_result", response_model=ExtractionResult, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_extraction_result(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		extraction_result = ExtractionResult(**data)
		extraction_result = handler.create(extraction_result)
		return extraction_result
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"extraction_result: {data} already exists")


@router.get(path="/idp/extraction_result", response_model=LimitOffsetPage[ExtractionResult], response_model_by_alias=False)
async def fetch_extraction_result(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, ExtractionResult)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	extraction_result = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(extraction_result))
	return create_page(extraction_result, total=handler.count(query=query), params=page)


@router.get(path="/idp/extraction_result/{id}", tags=["extraction_result"], response_model=ExtractionResult, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_extraction_result(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	extraction_result = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if extraction_result is None:
		raise HTTPException(status_code=404, detail=f"extraction_result {id} not found")
	return extraction_result


@router.put(path="/idp/extraction_result/{id}", tags=["extraction_result"], status_code=status.HTTP_200_OK)
async def update_extraction_result(id: str, data: Dict = Body):
	extraction_result = handler.get_by_id(id)
	if extraction_result is None:
		raise HTTPException(status_code=404, detail=f"extraction_result {id} not found")
	merged = extraction_result
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, ExtractionResult(**merged)):
		return JSONResponse(content={"extraction_result": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/extraction_result/{id}", tags=["extraction_result"], status_code=status.HTTP_202_ACCEPTED)
async def delete_extraction_result(id: str):
	if handler.delete(id):
		return JSONResponse(content={"extraction_result": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"extraction_result: {id} not found")


add_pagination(router)
