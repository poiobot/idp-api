from domain.model import ExtractionResult

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class ExtractionResultCrudCTL:
	"""
	ExtractionResult CRUD Controller - Handles CRUD operations for ExtractionResult entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, extraction_result: Union[ExtractionResult, Dict], reify: bool = True) -> Optional[ExtractionResult]:
		"""
		Register a new extraction_result

		Args:
			extraction_result: ExtractionResult object or dictionary with extraction_result data
			reify: If True, return ExtractionResult object; if False, return dictionary

		Returns:
			Created ExtractionResult object or dictionary, None if creation fails
		"""
		extraction_result = hooks.execute_sync(HookPoint.PRE_CREATE, "ExtractionResult", data=extraction_result)
		result = cls.dao.insert(entity=ExtractionResult, data=extraction_result, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "ExtractionResult", data=result)
		return result


	@classmethod
	def update(cls, extraction_result_id: str, extraction_result: Union[ExtractionResult, Dict], reify: bool = True) -> Optional[ExtractionResult]:
		"""
		Update an existing extraction_result

		Args:
			extraction_result_id: The extraction_result ID to update
			extraction_result: ExtractionResult object or dictionary with updated data
			reify: If True, return ExtractionResult object; if False, return dictionary

		Returns:
			Updated ExtractionResult object or dictionary
		"""
		extraction_result = hooks.execute_sync(HookPoint.PRE_UPDATE, "ExtractionResult", data=extraction_result)
		result = cls.dao.update(entity=ExtractionResult, id=extraction_result_id, data=extraction_result, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "ExtractionResult", data=result)
		return result

	@classmethod
	def get_by_id(cls, extraction_result_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[ExtractionResult]:
		"""
		Retrieve a extraction_result by its ID

		Args:
			extraction_result_id: The extraction_result ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return ExtractionResult object; if False, return dictionary

		Returns:
			ExtractionResult object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=ExtractionResult, id=extraction_result_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "ExtractionResult", data=result)
		return result

	@classmethod
	def get_list(cls, extraction_result_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[ExtractionResult, Dict]]:
		"""
		Retrieve multiple ExtractionResult by their IDs

		Args:
			extraction_result_ids: List of extraction_result IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return ExtractionResult objects; if False, return dictionaries

		Returns:
			Generator yielding ExtractionResult objects or dictionaries
		"""
		return cls.dao.find_list(entity=ExtractionResult, ids=extraction_result_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[ExtractionResult, Dict]]:
		"""
		Retrieve ExtractionResult by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return ExtractionResult objects; if False, return dictionaries

		Returns:
			Generator yielding ExtractionResult objects or dictionaries
		"""
		return cls.dao.fetch(entity=ExtractionResult, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[ExtractionResult, Dict]]:
		"""
		Retrieve ExtractionResult by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return ExtractionResult objects; if False, return dictionaries

		Returns:
			Generator yielding ExtractionResult objects or dictionaries
		"""
		return cls.dao.fetch(entity=ExtractionResult, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[ExtractionResult, Dict]]:
		"""
		Fetch ExtractionResult with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return ExtractionResult objects; if False, return dictionaries
			skip: Number of matching ExtractionResult to skip (the offset of a page)
			limit: Maximum number of ExtractionResult to return (default: all)

		Returns:
			Generator yielding ExtractionResult objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=ExtractionResult, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count ExtractionResult matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching ExtractionResult
		"""
		return cls.dao.count(entity=ExtractionResult, query=query)

	@classmethod
	def delete(cls, extraction_result_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a extraction_result by ID

		Args:
			extraction_result_id: The extraction_result ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "ExtractionResult", data=extraction_result_id)
		result = cls.dao.delete(entity=ExtractionResult, id=extraction_result_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "ExtractionResult", data=extraction_result_id)
		return result

	@classmethod
	def delete_list(cls, extraction_result_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple ExtractionResult by their IDs

		Args:
			extraction_result_ids: List of extraction_result IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of extraction_results deleted
		"""
		return cls.dao.delete_objects_list(
			entity=ExtractionResult,
			ids=extraction_result_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple ExtractionResult matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of extraction_results deleted
		"""
		return cls.dao.delete_many(entity=ExtractionResult, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all ExtractionResult (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of extraction_results deleted
		"""
		return cls.dao.delete_all(entity=ExtractionResult, physical_deletion=physical_delete)
