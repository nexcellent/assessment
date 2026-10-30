"""Unit tests for the shared sub-collection service.

One service serves every collection, so one module covers them: every case runs against
every collection, and a collection cannot be forgotten when the behaviour changes.
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import EntityNotFoundError
from app.core.exceptions import MandatoryFieldsMissingError
from app.core.exceptions import ProfileNotFoundError
from app.models.base import IdentifiedEntity
from app.models.profile import Education
from app.models.profile import ProjectBase
from app.models.profile import Skill
from app.models.profile import SkillCategory
from app.models.profile import WorkExperienceBase
from app.services import entity_collection_service as collections
from app.services.entity_collection_service import CollectionSpec
from app.services.entity_collection_service import EntityCollectionService

pytestmark = pytest.mark.unit

Case = tuple[CollectionSpec[Any], IdentifiedEntity]

# One valid entry per collection, paired with the spec that stores it.
CASES: tuple[Case, ...] = (
    (collections.WORK_EXPERIENCE, WorkExperienceBase(company="Acme", position="Dev", start_date="2020-01-01")),
    (collections.EDUCATION, Education(institution="MIT", degree="BSc", field_of_study="CS", start_date="2016-09-01")),
    (collections.PROJECTS, ProjectBase(title="Migration", role="Lead", start_date="2022-01-01")),
    (collections.SKILL_CATEGORIES, SkillCategory(category_name="Cloud", skills=[Skill(name="Azure", level="expert")])),
)


@pytest.fixture(params=CASES, ids=[spec.list_key for spec, _ in CASES])
def case(request: pytest.FixtureRequest) -> Case:
    """One collection under test, with a valid entry for it."""
    return request.param


@pytest.fixture
def service(case: Case, mock_profile_repository: AsyncMock) -> EntityCollectionService[Any]:
    return EntityCollectionService(mock_profile_repository, case[0])


@pytest.fixture
def profile_doc(case: Case) -> dict[str, Any]:
    """A profile already holding one entry of the collection, with the id ``e-1``."""
    spec, entry = case
    stored = entry.model_copy(update={"id": "e-1"}).model_dump(mode="json")
    return {"id": "p1", "personal_info": {"first_name": "Jane", "last_name": "Doe"}, spec.list_key: [stored]}


async def test_update_replaces_the_entry_and_keeps_its_id(
    case: Case, service: EntityCollectionService[Any], mock_profile_repository: AsyncMock, profile_doc: dict[str, Any]
) -> None:
    spec, entry = case
    mock_profile_repository.get.return_value = profile_doc

    item_id = await service.update("p1", "e-1", entry)

    assert item_id == "e-1"
    assert profile_doc[spec.list_key] == [entry.model_copy(update={"id": "e-1"}).model_dump(mode="json")]
    mock_profile_repository.replace.assert_awaited_once_with("p1", profile_doc)


async def test_an_unknown_entry_is_reported_and_nothing_is_written(
    case: Case, service: EntityCollectionService[Any], mock_profile_repository: AsyncMock, profile_doc: dict[str, Any]
) -> None:
    mock_profile_repository.get.return_value = profile_doc

    with pytest.raises(EntityNotFoundError):
        await service.update("p1", "nope", case[1])
    mock_profile_repository.replace.assert_not_awaited()


async def test_an_unknown_profile_is_reported(
    case: Case, service: EntityCollectionService[Any], mock_profile_repository: AsyncMock
) -> None:
    mock_profile_repository.get.return_value = None

    with pytest.raises(ProfileNotFoundError):
        await service.update("nope", "e-1", case[1])


@pytest.mark.parametrize(
    ("spec", "incomplete"),
    [
        (collections.WORK_EXPERIENCE, WorkExperienceBase(company="Acme")),
        (collections.EDUCATION, Education(institution="MIT")),
        (collections.PROJECTS, ProjectBase(title="Migration")),
    ],
    ids=["work_experience", "education", "projects"],
)
async def test_an_entry_with_empty_mandatory_fields_is_refused_before_any_read(
    spec: CollectionSpec[Any], incomplete: IdentifiedEntity, mock_profile_repository: AsyncMock
) -> None:
    service: EntityCollectionService[Any] = EntityCollectionService(mock_profile_repository, spec)

    with pytest.raises(MandatoryFieldsMissingError) as excinfo:
        await service.update("p1", "e-1", incomplete)

    assert excinfo.value.fields == list(spec.model.MANDATORY[1:])
    mock_profile_repository.get.assert_not_awaited()
