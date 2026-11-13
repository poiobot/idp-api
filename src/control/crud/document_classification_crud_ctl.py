from domain.model import DocumentClassification

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class DocumentClassificationCrudCTL:
	"""
	DocumentClassification CRUD Controller - Handles CRUD operations for DocumentClassification entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, document_classification: Union[DocumentClassification, Dict], reify: bool = True) -> Optional[DocumentClassification]:
		"""
		Register a new document_classification

		Args:
			document_classification: DocumentClassification object or dictionary with document_classification data
			reify: If True, return DocumentClassification object; if False, return dictionary

		Returns:
			Created DocumentClassification object or dictionary, None if creation fails
		"""
		document_classification = hooks.execute_sync(HookPoint.PRE_CREATE, "DocumentClassification", data=document_classification)
		result = cls.dao.insert(entity=DocumentClassification, data=document_classification, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "DocumentClassification", data=result)
		return result


	@classmethod
	def update(cls, document_classification_id: str, document_classification: Union[DocumentClassification, Dict], reify: bool = True) -> Optional[DocumentClassification]:
		"""
		Update an existing document_classification

		Args:
			document_classification_id: The document_classification ID to update
			document_classification: DocumentClassification object or dictionary with updated data
			reify: If True, return DocumentClassification object; if False, return dictionary

		Returns:
			Updated DocumentClassification object or dictionary
		"""
		document_classification = hooks.execute_sync(HookPoint.PRE_UPDATE, "DocumentClassification", data=document_classification)
		result = cls.dao.update(entity=DocumentClassification, id=document_classification_id, data=document_classification, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "DocumentClassification", data=result)
		return result

	@classmethod
	def get_by_id(cls, document_classification_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[DocumentClassification]:
		"""
		Retrieve a document_classification by its ID

		Args:
			document_classification_id: The document_classification ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return DocumentClassification object; if False, return dictionary

		Returns:
			DocumentClassification object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=DocumentClassification, id=document_classification_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "DocumentClassification", data=result)
		return result

	@classmethod
	def get_list(cls, document_classification_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[DocumentClassification, Dict]]:
		"""
		Retrieve multiple DocumentClassification by their IDs

		Args:
			document_classification_ids: List of document_classification IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return DocumentClassification objects; if False, return dictionaries

		Returns:
			Generator yielding DocumentClassification objects or dictionaries
		"""
		return cls.dao.find_list(entity=DocumentClassification, ids=document_classification_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[DocumentClassification, Dict]]:
		"""
		Retrieve DocumentClassification by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return DocumentClassification objects; if False, return dictionaries

		Returns:
			Generator yielding DocumentClassification objects or dictionaries
		"""
		return cls.dao.fetch(entity=DocumentClassification, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[DocumentClassification, Dict]]:
		"""
		Retrieve DocumentClassification by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return DocumentClassification objects; if False, return dictionaries

		Returns:
			Generator yielding DocumentClassification objects or dictionaries
		"""
		return cls.dao.fetch(entity=DocumentClassification, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[DocumentClassification, Dict]]:
		"""
		Fetch DocumentClassification with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return DocumentClassification objects; if False, return dictionaries
			skip: Number of matching DocumentClassification to skip (the offset of a page)
			limit: Maximum number of DocumentClassification to return (default: all)

		Returns:
			Generator yielding DocumentClassification objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=DocumentClassification, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count DocumentClassification matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching DocumentClassification
		"""
		return cls.dao.count(entity=DocumentClassification, query=query)

	@classmethod
	def delete(cls, document_classification_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a document_classification by ID

		Args:
			document_classification_id: The document_classification ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "DocumentClassification", data=document_classification_id)
		result = cls.dao.delete(entity=DocumentClassification, id=document_classification_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "DocumentClassification", data=document_classification_id)
		return result

	@classmethod
	def delete_list(cls, document_classification_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple DocumentClassification by their IDs

		Args:
			document_classification_ids: List of document_classification IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of document_classifications deleted
		"""
		return cls.dao.delete_objects_list(
			entity=DocumentClassification,
			ids=document_classification_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple DocumentClassification matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of document_classifications deleted
		"""
		return cls.dao.delete_many(entity=DocumentClassification, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all DocumentClassification (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of document_classifications deleted
		"""
		return cls.dao.delete_all(entity=DocumentClassification, physical_deletion=physical_delete)
