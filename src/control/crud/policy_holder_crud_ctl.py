from domain.model import PolicyHolder

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class PolicyHolderCrudCTL:
	"""
	PolicyHolder CRUD Controller - Handles CRUD operations for PolicyHolder entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, policy_holder: Union[PolicyHolder, Dict], reify: bool = True) -> Optional[PolicyHolder]:
		"""
		Register a new policy_holder

		Args:
			policy_holder: PolicyHolder object or dictionary with policy_holder data
			reify: If True, return PolicyHolder object; if False, return dictionary

		Returns:
			Created PolicyHolder object or dictionary, None if creation fails
		"""
		policy_holder = hooks.execute_sync(HookPoint.PRE_CREATE, "PolicyHolder", data=policy_holder)
		result = cls.dao.insert(entity=PolicyHolder, data=policy_holder, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "PolicyHolder", data=result)
		return result


	@classmethod
	def update(cls, policy_holder_id: str, policy_holder: Union[PolicyHolder, Dict], reify: bool = True) -> Optional[PolicyHolder]:
		"""
		Update an existing policy_holder

		Args:
			policy_holder_id: The policy_holder ID to update
			policy_holder: PolicyHolder object or dictionary with updated data
			reify: If True, return PolicyHolder object; if False, return dictionary

		Returns:
			Updated PolicyHolder object or dictionary
		"""
		policy_holder = hooks.execute_sync(HookPoint.PRE_UPDATE, "PolicyHolder", data=policy_holder)
		result = cls.dao.update(entity=PolicyHolder, id=policy_holder_id, data=policy_holder, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "PolicyHolder", data=result)
		return result

	@classmethod
	def get_by_id(cls, policy_holder_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[PolicyHolder]:
		"""
		Retrieve a policy_holder by its ID

		Args:
			policy_holder_id: The policy_holder ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return PolicyHolder object; if False, return dictionary

		Returns:
			PolicyHolder object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=PolicyHolder, id=policy_holder_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "PolicyHolder", data=result)
		return result

	@classmethod
	def get_list(cls, policy_holder_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[PolicyHolder, Dict]]:
		"""
		Retrieve multiple PolicyHolder by their IDs

		Args:
			policy_holder_ids: List of policy_holder IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return PolicyHolder objects; if False, return dictionaries

		Returns:
			Generator yielding PolicyHolder objects or dictionaries
		"""
		return cls.dao.find_list(entity=PolicyHolder, ids=policy_holder_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[PolicyHolder, Dict]]:
		"""
		Retrieve PolicyHolder by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return PolicyHolder objects; if False, return dictionaries

		Returns:
			Generator yielding PolicyHolder objects or dictionaries
		"""
		return cls.dao.fetch(entity=PolicyHolder, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[PolicyHolder, Dict]]:
		"""
		Retrieve PolicyHolder by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return PolicyHolder objects; if False, return dictionaries

		Returns:
			Generator yielding PolicyHolder objects or dictionaries
		"""
		return cls.dao.fetch(entity=PolicyHolder, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[PolicyHolder, Dict]]:
		"""
		Fetch PolicyHolder with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return PolicyHolder objects; if False, return dictionaries
			skip: Number of matching PolicyHolder to skip (the offset of a page)
			limit: Maximum number of PolicyHolder to return (default: all)

		Returns:
			Generator yielding PolicyHolder objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=PolicyHolder, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count PolicyHolder matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching PolicyHolder
		"""
		return cls.dao.count(entity=PolicyHolder, query=query)

	@classmethod
	def delete(cls, policy_holder_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a policy_holder by ID

		Args:
			policy_holder_id: The policy_holder ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "PolicyHolder", data=policy_holder_id)
		result = cls.dao.delete(entity=PolicyHolder, id=policy_holder_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "PolicyHolder", data=policy_holder_id)
		return result

	@classmethod
	def delete_list(cls, policy_holder_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple PolicyHolder by their IDs

		Args:
			policy_holder_ids: List of policy_holder IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of policy_holders deleted
		"""
		return cls.dao.delete_objects_list(
			entity=PolicyHolder,
			ids=policy_holder_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple PolicyHolder matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of policy_holders deleted
		"""
		return cls.dao.delete_many(entity=PolicyHolder, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all PolicyHolder (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of policy_holders deleted
		"""
		return cls.dao.delete_all(entity=PolicyHolder, physical_deletion=physical_delete)
