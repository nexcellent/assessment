"""Dependency injection container for the application.

Internal ``_get_*()`` functions build the singletons; the public ``get_*_di()`` coroutine
is what ``Depends()`` takes. The collection providers are the exception: one plain cached
function each, which is handed to ``Depends()`` directly.
"""

from functools import lru_cache

from app.core.settings import get_settings
from app.models.profile import Education
from app.models.profile import ProjectBase
from app.models.profile import SkillCategory
from app.models.profile import WorkExperienceBase
from app.repositories.interfaces import IProfileRepository
from app.repositories.profile_repository import MemoryProfileRepository
from app.services import entity_collection_service as collections
from app.services.entity_collection_service import EntityCollectionService
from app.services.interfaces import IProfileService
from app.services.profile_service import ProfileService


@lru_cache(maxsize=1)
def _get_profile_repository() -> IProfileRepository:
    """Get cached profile repository instance."""
    return MemoryProfileRepository(get_settings().fixtures_dir)


@lru_cache(maxsize=1)
def _get_profile_service() -> IProfileService:
    """Get cached profile service instance."""
    return ProfileService(profile_repository=_get_profile_repository())


@lru_cache(maxsize=1)
def get_work_experience_service_di() -> EntityCollectionService[WorkExperienceBase]:
    """Dependency injection for the work experience collection."""
    return EntityCollectionService(_get_profile_repository(), collections.WORK_EXPERIENCE)


@lru_cache(maxsize=1)
def get_education_service_di() -> EntityCollectionService[Education]:
    """Dependency injection for the education collection."""
    return EntityCollectionService(_get_profile_repository(), collections.EDUCATION)


@lru_cache(maxsize=1)
def get_project_service_di() -> EntityCollectionService[ProjectBase]:
    """Dependency injection for the project collection."""
    return EntityCollectionService(_get_profile_repository(), collections.PROJECTS)


@lru_cache(maxsize=1)
def get_skill_category_service_di() -> EntityCollectionService[SkillCategory]:
    """Dependency injection for the skill category collection."""
    return EntityCollectionService(_get_profile_repository(), collections.SKILL_CATEGORIES)


async def get_profile_service_di() -> IProfileService:
    """Dependency injection for profile service."""
    return _get_profile_service()


def get_profile_repository() -> IProfileRepository:
    """The profile repository outside a request, for the health check."""
    return _get_profile_repository()
