"""Base service with shared helpers for entity manipulation."""

from typing import Any

from app.core.exceptions import EntityNotFoundError
from app.core.exceptions import MandatoryFieldsMissingError
from app.core.exceptions import ProfileNotFoundError
from app.models.base import BaseEntity
from app.repositories.interfaces import IProfileRepository


def require_complete(entity: BaseEntity, label: str) -> None:
    """Refuse a write that leaves a mandatory field empty.

    The models let those fields be empty so that a CV import can store what the CV
    gives (``BaseEntity.MANDATORY``); every write after it fills them.
    """
    missing = entity.missing_mandatory()
    if missing:
        raise MandatoryFieldsMissingError(label, missing)


class BaseEntityService:
    """Shared functionality for all entity services.

    Provides common helpers for profile-level document retrieval and in-place list
    manipulation on the stored documents.
    """

    def __init__(self, repository: IProfileRepository) -> None:
        """Initialize with a profile repository."""
        self._repo = repository

    async def _require_profile(self, profile_id: str) -> dict[str, Any]:
        """Get profile dict or raise ProfileNotFoundError."""
        doc = await self._repo.get(profile_id)
        if doc is None:
            raise ProfileNotFoundError(profile_id)
        return doc

    @staticmethod
    def _replace_in_list(
        doc: dict[str, Any],
        field: str,
        item_id: str,
        new_value: Any,
        *,
        profile_id: str = "",
    ) -> None:
        """Find an item by ID in a list field and replace it.

        Raises:
            EntityNotFoundError: If the item with the given ID is not found.

        """
        items = doc.get(field, [])
        for i, item in enumerate(items):
            if item.get("id") == item_id:
                updated = new_value.model_copy(update={"id": item_id})
                items[i] = updated.model_dump(mode="json")
                return
        raise EntityNotFoundError(field, item_id, profile_id)
