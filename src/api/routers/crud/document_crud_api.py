from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, create_page, resolve_params, LimitOffsetPage
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from typing import List, Dict

from lib.spore_tools import SporeTools as tools
from lib.httptools import HttpTools, QueryParser
from control.crud.document_crud_ctl import DocumentCrudCTL
from domain.document import Document

disable_installed_extensions_check()

router = APIRouter()
handler = DocumentCrudCTL()

# Reference fields that ?expand= can replace with the referenced documents
EXPANDABLE = ("holderId", "policyId",)
EXPAND_HELP = "Comma-separated reference fields to replace with the referenced documents: holderId, policyId"


@router.post(path="/idp/document", response_model=Document, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def create_document(data: Dict = Body):
	try:
		data["id"] = data.get("id", None)
		document = Document(**data)
		document = handler.create(document)
		return document
	except ValidationError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"incorrect input data: {data}")
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"document: {data} already exists")


@router.get(path="/idp/document", response_model=LimitOffsetPage[Document], response_model_by_alias=False)
async def fetch_document(q: List[str] = Query(None), keys: str = "*", expand: str = Query(None, description=EXPAND_HELP)):
	keys = "*" if keys == "*" else {key: 1 for key in keys.split(",")}
	query = None if q is None else QueryParser.transform_query_conditions(q, Document)
	expand = HttpTools.parse_expand(expand, EXPANDABLE)
	# ?limit= and ?offset= (read by add_pagination) go to the database, which returns only this page
	page = resolve_params()
	document = list(handler.fetch(query=query, keys=keys, expand=expand, reify=True if keys == "*" else False, skip=page.offset, limit=page.limit))
	if keys != "*":
		return JSONResponse(content=HttpTools.json_content(document))
	return create_page(document, total=handler.count(query=query), params=page)


@router.get(path="/idp/document/{id}", tags=["document"], response_model=Document, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def find_document(id: str, expand: str = Query(None, description=EXPAND_HELP)):
	document = handler.get_by_id(id, expand=HttpTools.parse_expand(expand, EXPANDABLE))
	if document is None:
		raise HTTPException(status_code=404, detail=f"document {id} not found")
	return document


@router.put(path="/idp/document/{id}", tags=["document"], status_code=status.HTTP_200_OK)
async def update_document(id: str, data: Dict = Body):
	document = handler.get_by_id(id)
	if document is None:
		raise HTTPException(status_code=404, detail=f"document {id} not found")
	merged = document
	if isinstance(merged, dict):
		merged.update(data)
	else:
		merged = merged.model_dump()
		merged.update(data)
	if handler.update(id, Document(**merged)):
		return JSONResponse(content={"document": data, "status": "UPDATED"}, status_code=status.HTTP_200_OK)


@router.delete(path="/idp/document/{id}", tags=["document"], status_code=status.HTTP_202_ACCEPTED)
async def delete_document(id: str):
	if handler.delete(id):
		return JSONResponse(content={"document": id, "status": "DELETED"}, status_code=status.HTTP_200_OK)
	else:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"document: {id} not found")


add_pagination(router)
