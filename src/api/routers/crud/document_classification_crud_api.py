from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.document_classification_crud_ctl import DocumentClassificationCrudCTL
from domain.document_classification import DocumentClassification

disable_installed_extensions_check()

router = APIRouter()
handler = DocumentClassificationCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ("fileId",)
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: fileId"


@router.post(path="/idp/document_classification", response_model=DocumentClassification, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_document_classification(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		document_classification = DocumentClassification(**data)
		document_classification = handler.create(document_classification)
		return document_classification
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"document_classification: {data} already exists")


@router.get(path="/idp/document_classification", response_model=LimitOffsetPage[DocumentClassification], response_model_by_alias=False)
async def fetch_document_classification(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, DocumentClassification)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	document_classification = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(document_classification))
	return create_page(document_classification, total=handler.count(query=query), params=page)


@router.get(path="/idp/document_classification/{id}", tags=["document_classification"], response_model=DocumentClassification, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_document_classification(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	document_classification = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if document_classification is None:
		raise HTTPException(status_code=404, detail=f"document_classification {id} not found")
	return document_classification


@router.put(path="/idp/document_classification/{id}", tags=["document_classification"], status_code=status.HTTP_200_OK)
async def update_document_classification(id: str, data: Dict = Body):
	document_classification = handler.get_by_id(id)
	if document_classification is None:
		raise HTTPException(status_code=404, detail=f"document_classification {id} not found")
	merged = document_classification
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, DocumentClassification(**merged)):
		return JSONResponse(content={"document_classification": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/document_classification/{id}", tags=["document_classification"], status_code=status.HTTP_202_ACCEPTED)
async def delete_document_classification(id: str):
	if handler.delete(id):
		return JSONResponse(content={"document_classification": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"document_classification: {id} not found")


add_pagination(router)
