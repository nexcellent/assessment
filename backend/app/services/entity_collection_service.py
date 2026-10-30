"""One service for every repeated sub-collection of a profile.

Work experience, education, projects and skill categories are all stored the same
way — a list of entity documents on the profile — and differ only in the list key and
the entity type. The shape lives here once; :data:`COLLECTIONS` names every collection
it applies to.
"""

from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

from app.core.logging import get_logger
from app.models.base import IdentifiedEntity
from app.models.profile import Education
from app.models.profile import ProjectBase
from app.models.profile import SkillCategory
from app.models.profile import WorkExperienceBase
from app.repositories.interfaces import IProfileRepository
from app.services.base_entity_service import BaseEntityService
from app.services.base_entity_service import require_complete

logger = get_logger(__name__)

# The spec only hands its model out, so it may be read as a spec of any supertype;
# the service takes entities in as well and has to stay invariant.
T_co = TypeVar("T_co", bound=IdentifiedEntity, covariant=True)
T = TypeVar("T", bound=IdentifiedEntity)


@dataclass(frozen=True)
class CollectionSpec(Generic[T_co]):
    """Where a sub-collection lives on the profile document and what it holds.

    ``label`` is the entity as a person reads it. It goes into the log line and into
    the error message, which is why "skill category" carries its space.
    """

    list_key: str
    model: type[T_co]
    label: str


class EntityCollectionService(BaseEntityService, Generic[T]):
    """Replace entries of one profile sub-collection."""

    def __init__(self, repository: IProfileRepository, spec: CollectionSpec[T]) -> None:
        """Bind the service to the collection it serves."""
        super().__init__(repository)
        self.spec = spec

    async def update(self, profile_id: str, item_id: str, item: T) -> str:
        """Replace the entry with the given id."""
        require_complete(item, self.spec.label)
        doc = await self._require_profile(profile_id)
        self._replace_in_list(doc, self.spec.list_key, item_id, item, profile_id=profile_id)
        await self._repo.replace(profile_id, doc)
        logger.info("Updated %s %s in profile %s", self.spec.label, item_id, profile_id)
        return item_id


WORK_EXPERIENCE = CollectionSpec("work_experience", WorkExperienceBase, "work experience")
EDUCATION = CollectionSpec("education", Education, "education")
PROJECTS = CollectionSpec("projects", ProjectBase, "project")
SKILL_CATEGORIES = CollectionSpec("skill_categories", SkillCategory, "skill category")

COLLECTIONS: tuple[CollectionSpec[IdentifiedEntity], ...] = (
    WORK_EXPERIENCE,
    EDUCATION,
    PROJECTS,
    SKILL_CATEGORIES,
)
