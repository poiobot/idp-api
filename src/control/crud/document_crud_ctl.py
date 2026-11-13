from domain.model import Document

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class DocumentCrudCTL:
	"""
	Document CRUD Controller - Handles CRUD operations for Document entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, document: Union[Document, Dict], reify: bool = True) -> Optional[Document]:
		"""
		Register a new document

		Args:
			document: Document object or dictionary with document data
			reify: If True, return Document object; if False, return dictionary

		Returns:
			Created Document object or dictionary, None if creation fails
		"""
		document = hooks.execute_sync(HookPoint.PRE_CREATE, "Document", data=document)
		result = cls.dao.insert(entity=Document, data=document, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "Document", data=result)
		return result


	@classmethod
	def update(cls, document_id: str, document: Union[Document, Dict], reify: bool = True) -> Optional[Document]:
		"""
		Update an existing document

		Args:
			document_id: The document ID to update
			document: Document object or dictionary with updated data
			reify: If True, return Document object; if False, return dictionary

		Returns:
			Updated Document object or dictionary
		"""
		document = hooks.execute_sync(HookPoint.PRE_UPDATE, "Document", data=document)
		result = cls.dao.update(entity=Document, id=document_id, data=document, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "Document", data=result)
		return result

	@classmethod
	def get_by_id(cls, document_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[Document]:
		"""
		Retrieve a document by its ID

		Args:
			document_id: The document ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return Document object; if False, return dictionary

		Returns:
			Document object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=Document, id=document_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "Document", data=result)
		return result

	@classmethod
	def get_list(cls, document_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[Document, Dict]]:
		"""
		Retrieve multiple Document by their IDs

		Args:
			document_ids: List of document IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Document objects; if False, return dictionaries

		Returns:
			Generator yielding Document objects or dictionaries
		"""
		return cls.dao.find_list(entity=Document, ids=document_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[Document, Dict]]:
		"""
		Retrieve Document by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Document objects; if False, return dictionaries

		Returns:
			Generator yielding Document objects or dictionaries
		"""
		return cls.dao.fetch(entity=Document, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[Document, Dict]]:
		"""
		Retrieve Document by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Document objects; if False, return dictionaries

		Returns:
			Generator yielding Document objects or dictionaries
		"""
		return cls.dao.fetch(entity=Document, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[Document, Dict]]:
		"""
		Fetch Document with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return Document objects; if False, return dictionaries
			skip: Number of matching Document to skip (the offset of a page)
			limit: Maximum number of Document to return (default: all)

		Returns:
			Generator yielding Document objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=Document, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count Document matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching Document
		"""
		return cls.dao.count(entity=Document, query=query)

	@classmethod
	def delete(cls, document_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a document by ID

		Args:
			document_id: The document ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "Document", data=document_id)
		result = cls.dao.delete(entity=Document, id=document_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "Document", data=document_id)
		return result

	@classmethod
	def delete_list(cls, document_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple Document by their IDs

		Args:
			document_ids: List of document IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of documents deleted
		"""
		return cls.dao.delete_objects_list(
			entity=Document,
			ids=document_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple Document matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of documents deleted
		"""
		return cls.dao.delete_many(entity=Document, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all Document (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of documents deleted
		"""
		return cls.dao.delete_all(entity=Document, physical_deletion=physical_delete)
