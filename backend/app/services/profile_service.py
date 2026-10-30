"""Profile service — the profile as a whole.

Reads one profile and lists overviews. The repeated sub-collections live in
``EntityCollectionService`` instead.
"""

from typing import Any

from app.models.profile import Profile
from app.models.profile import ProfileOverview
from app.repositories.interfaces import IProfileRepository
from app.services.base_entity_service import BaseEntityService
from app.services.interfaces import IProfileService

# The list reads every document; the overview is shaped from it in the service.
PROFILE_LIST_QUERY = "SELECT * FROM c"


class ProfileService(IProfileService, BaseEntityService):
    """Profile-level business operations."""

    def __init__(self, *, profile_repository: IProfileRepository) -> None:
        """Initialize the ProfileService."""
        # BaseEntityService needs the repository as self._repo
        BaseEntityService.__init__(self, repository=profile_repository)

    # --- internal helpers ---

    def _to_overview(self, doc: dict[str, Any]) -> ProfileOverview:
        """Reduce a stored document to what the list shows."""
        profile = Profile.model_validate(doc)
        return ProfileOverview(
            id=profile.id,
            first_name=profile.personal_info.first_name,
            last_name=profile.personal_info.last_name,
            title=profile.personal_info.title,
            incomplete=bool(profile.missing_fields),
        )

    # --- reads ---

    async def get_profile(self, profile_id: str) -> Profile | None:
        """Get a complete profile by ID. Returns None if not found."""
        doc = await self._repo.get(profile_id)
        if doc is None:
            return None
        return Profile.model_validate(doc)

    async def list_profiles(self, limit: int = 100, offset: int = 0) -> tuple[list[ProfileOverview], int]:
        """List profile overviews with pagination, in the store's order."""
        documents = await self._repo.query(PROFILE_LIST_QUERY)
        page = documents[offset : offset + limit]
        return [self._to_overview(doc) for doc in page], len(documents)
