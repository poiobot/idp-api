from domain.model import InsurancePolicy

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class InsurancePolicyCrudCTL:
	"""
	InsurancePolicy CRUD Controller - Handles CRUD operations for InsurancePolicy entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, insurance_policy: Union[InsurancePolicy, Dict], reify: bool = True) -> Optional[InsurancePolicy]:
		"""
		Register a new insurance_policy

		Args:
			insurance_policy: InsurancePolicy object or dictionary with insurance_policy data
			reify: If True, return InsurancePolicy object; if False, return dictionary

		Returns:
			Created InsurancePolicy object or dictionary, None if creation fails
		"""
		insurance_policy = hooks.execute_sync(HookPoint.PRE_CREATE, "InsurancePolicy", data=insurance_policy)
		result = cls.dao.insert(entity=InsurancePolicy, data=insurance_policy, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "InsurancePolicy", data=result)
		return result


	@classmethod
	def update(cls, insurance_policy_id: str, insurance_policy: Union[InsurancePolicy, Dict], reify: bool = True) -> Optional[InsurancePolicy]:
		"""
		Update an existing insurance_policy

		Args:
			insurance_policy_id: The insurance_policy ID to update
			insurance_policy: InsurancePolicy object or dictionary with updated data
			reify: If True, return InsurancePolicy object; if False, return dictionary

		Returns:
			Updated InsurancePolicy object or dictionary
		"""
		insurance_policy = hooks.execute_sync(HookPoint.PRE_UPDATE, "InsurancePolicy", data=insurance_policy)
		result = cls.dao.update(entity=InsurancePolicy, id=insurance_policy_id, data=insurance_policy, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "InsurancePolicy", data=result)
		return result

	@classmethod
	def get_by_id(cls, insurance_policy_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[InsurancePolicy]:
		"""
		Retrieve a insurance_policy by its ID

		Args:
			insurance_policy_id: The insurance_policy ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return InsurancePolicy object; if False, return dictionary

		Returns:
			InsurancePolicy object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=InsurancePolicy, id=insurance_policy_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "InsurancePolicy", data=result)
		return result

	@classmethod
	def get_list(cls, insurance_policy_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[InsurancePolicy, Dict]]:
		"""
		Retrieve multiple InsurancePolicy by their IDs

		Args:
			insurance_policy_ids: List of insurance_policy IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return InsurancePolicy objects; if False, return dictionaries

		Returns:
			Generator yielding InsurancePolicy objects or dictionaries
		"""
		return cls.dao.find_list(entity=InsurancePolicy, ids=insurance_policy_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[InsurancePolicy, Dict]]:
		"""
		Retrieve InsurancePolicy by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return InsurancePolicy objects; if False, return dictionaries

		Returns:
			Generator yielding InsurancePolicy objects or dictionaries
		"""
		return cls.dao.fetch(entity=InsurancePolicy, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[InsurancePolicy, Dict]]:
		"""
		Retrieve InsurancePolicy by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return InsurancePolicy objects; if False, return dictionaries

		Returns:
			Generator yielding InsurancePolicy objects or dictionaries
		"""
		return cls.dao.fetch(entity=InsurancePolicy, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[InsurancePolicy, Dict]]:
		"""
		Fetch InsurancePolicy with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return InsurancePolicy objects; if False, return dictionaries
			skip: Number of matching InsurancePolicy to skip (the offset of a page)
			limit: Maximum number of InsurancePolicy to return (default: all)

		Returns:
			Generator yielding InsurancePolicy objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=InsurancePolicy, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count InsurancePolicy matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching InsurancePolicy
		"""
		return cls.dao.count(entity=InsurancePolicy, query=query)

	@classmethod
	def delete(cls, insurance_policy_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a insurance_policy by ID

		Args:
			insurance_policy_id: The insurance_policy ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "InsurancePolicy", data=insurance_policy_id)
		result = cls.dao.delete(entity=InsurancePolicy, id=insurance_policy_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "InsurancePolicy", data=insurance_policy_id)
		return result

	@classmethod
	def delete_list(cls, insurance_policy_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple InsurancePolicy by their IDs

		Args:
			insurance_policy_ids: List of insurance_policy IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of insurance_policys deleted
		"""
		return cls.dao.delete_objects_list(
			entity=InsurancePolicy,
			ids=insurance_policy_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple InsurancePolicy matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of insurance_policys deleted
		"""
		return cls.dao.delete_many(entity=InsurancePolicy, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all InsurancePolicy (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of insurance_policys deleted
		"""
		return cls.dao.delete_all(entity=InsurancePolicy, physical_deletion=physical_delete)
