from domain.model import Claim

from typing import List, Dict, Union, Optional, Any, Tuple
from data.generic_dao import GenericDAO
from lib.hooks import hooks, HookPoint


class ClaimCrudCTL:
	"""
	Claim CRUD Controller - Handles CRUD operations for Claim entities
	Uses GenericDAO for database-agnostic operations
	"""

	dao = GenericDAO()

	@classmethod
	def create(cls, claim: Union[Claim, Dict], reify: bool = True) -> Optional[Claim]:
		"""
		Register a new claim

		Args:
			claim: Claim object or dictionary with claim data
			reify: If True, return Claim object; if False, return dictionary

		Returns:
			Created Claim object or dictionary, None if creation fails
		"""
		claim = hooks.execute_sync(HookPoint.PRE_CREATE, "Claim", data=claim)
		result = cls.dao.insert(entity=Claim, data=claim, reify=reify)
		hooks.execute_sync(HookPoint.POST_CREATE, "Claim", data=result)
		return result


	@classmethod
	def update(cls, claim_id: str, claim: Union[Claim, Dict], reify: bool = True) -> Optional[Claim]:
		"""
		Update an existing claim

		Args:
			claim_id: The claim ID to update
			claim: Claim object or dictionary with updated data
			reify: If True, return Claim object; if False, return dictionary

		Returns:
			Updated Claim object or dictionary
		"""
		claim = hooks.execute_sync(HookPoint.PRE_UPDATE, "Claim", data=claim)
		result = cls.dao.update(entity=Claim, id=claim_id, data=claim, reify=reify)
		hooks.execute_sync(HookPoint.POST_UPDATE, "Claim", data=result)
		return result

	@classmethod
	def get_by_id(cls, claim_id: str, keys: List[str] = "*", expand: Optional[List[str]] = None, reify: bool = True) -> Optional[Claim]:
		"""
		Retrieve a claim by its ID

		Args:
			claim_id: The claim ID to search for
			keys: List of fields to retrieve (default: all fields)
			expand: List of reference fields to expand/join
			reify: If True, return Claim object; if False, return dictionary

		Returns:
			Claim object or dictionary, None if not found
		"""
		result = cls.dao.find_by_id(entity=Claim, id=claim_id, keys=keys, expand=expand, reify=reify)
		result = hooks.execute_sync(HookPoint.POST_FETCH, "Claim", data=result)
		return result

	@classmethod
	def get_list(cls, claim_ids: List[str], keys: List[str] = "*", expand: List[str]=None, reify: bool = True) -> List[Union[Claim, Dict]]:
		"""
		Retrieve multiple Claim by their IDs

		Args:
			claim_ids: List of claim IDs to retrieve
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Claim objects; if False, return dictionaries

		Returns:
			Generator yielding Claim objects or dictionaries
		"""
		return cls.dao.find_list(entity=Claim, ids=claim_ids, keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[Claim, Dict]]:
		"""
		Retrieve Claim by key-value

		Args:
			key: The field name to search
			value: The value to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Claim objects; if False, return dictionaries

		Returns:
			Generator yielding Claim objects or dictionaries
		"""
		return cls.dao.fetch(entity=Claim, query=[(key, "==", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def get_by_key_value_like(cls, key: str, value: Any, keys: List[str]="*", expand: List[str] = None, reify: bool=True) -> List[Union[Claim, Dict]]:
		"""
		Retrieve Claim by key-value with LIKE operator

		Args:
			key: The field name to search
			value: The value pattern to match
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			reify: If True, return Claim objects; if False, return dictionaries

		Returns:
			Generator yielding Claim objects or dictionaries
		"""
		return cls.dao.fetch(entity=Claim, query=[(key, "like", value)], keys=keys, expand=expand, reify=reify)

	@classmethod
	def fetch(cls, query: Optional[List[Tuple]]=None, expand: Optional[List[str]]=None, keys: List[str]="*", sort_by: Optional[List[Tuple[str, int]]]=None, reify: bool=True, skip: int=0, limit: Optional[int]=None) -> List[Union[Claim, Dict]]:
		"""
		Fetch Claim with custom query, expansion, sorting and paging

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			expand: List of reference fields to expand/join
			keys: List of fields to retrieve (default: all fields)
			sort_by: List of tuples for sorting [('field', 1/-1), ...] (1=asc, -1=desc)
			reify: If True, return Claim objects; if False, return dictionaries
			skip: Number of matching Claim to skip (the offset of a page)
			limit: Maximum number of Claim to return (default: all)

		Returns:
			Generator yielding Claim objects or dictionaries, read from the database as consumed
		"""
		return cls.dao.fetch(entity=Claim, query=query, expand=expand, keys=keys, sort_by=sort_by, reify=reify, skip=skip, limit=limit)

	@classmethod
	def count(cls, query: Optional[List[Tuple]]=None) -> int:
		"""
		Count Claim matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]

		Returns:
			Number of matching Claim
		"""
		return cls.dao.count(entity=Claim, query=query)

	@classmethod
	def delete(cls, claim_id: str, physical_delete: bool = True) -> bool:
		"""
		Delete a claim by ID

		Args:
			claim_id: The claim ID to delete
			physical_delete: If True, permanently delete; if False, soft delete (mark as inactive)

		Returns:
			True if deletion successful, False otherwise
		"""
		hooks.execute_sync(HookPoint.PRE_DELETE, "Claim", data=claim_id)
		result = cls.dao.delete(entity=Claim, id=claim_id, physical_delete=physical_delete)
		hooks.execute_sync(HookPoint.POST_DELETE, "Claim", data=claim_id)
		return result

	@classmethod
	def delete_list(cls, claim_ids: List[str], physical_delete: bool = True) -> int:
		"""
		Delete multiple Claim by their IDs

		Args:
			claim_ids: List of claim IDs to delete
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of claims deleted
		"""
		return cls.dao.delete_objects_list(
			entity=Claim,
			ids=claim_ids,
			physical_deletion=physical_delete
		)

	@classmethod
	def delete_many(cls, query: Optional[List[Tuple]] = None, physical_delete: bool = True) -> int:
		"""
		Delete multiple Claim matching a query

		Args:
			query: List of tuples with query conditions [('key', 'operator', 'value'), ...]
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of claims deleted
		"""
		return cls.dao.delete_many(entity=Claim, query=query, physical_delete=physical_delete)

	@classmethod
	def delete_all(cls, physical_delete: bool = False) -> int:
		"""
		Delete all Claim (use with caution!)

		Args:
			physical_delete: If True, permanently delete; if False, soft delete

		Returns:
			Number of claims deleted
		"""
		return cls.dao.delete_all(entity=Claim, physical_deletion=physical_delete)
