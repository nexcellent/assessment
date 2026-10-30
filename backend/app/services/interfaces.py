"""Service interfaces for the application.

Defines the abstract contract of the service with behaviour of its own; the
implementation is wired via the DI container in ``app.core.container``. The
sub-collections have no interface here: they are all served by the one concrete
``EntityCollectionService``, parameterised by a ``CollectionSpec``.
"""

from abc import ABC
from abc import abstractmethod

from app.models.profile import Profile
from app.models.profile import ProfileOverview


class IProfileService(ABC):
    """Interface for profile business operations."""

    @abstractmethod
    async def get_profile(self, profile_id: str) -> Profile | None:
        """Get a complete profile by ID. Returns None if not found."""

    @abstractmethod
    async def list_profiles(self, limit: int = 100, offset: int = 0) -> tuple[list[ProfileOverview], int]:
        """List profile overviews with pagination.

        Returns:
            A tuple of (profiles, total_count).
        """
