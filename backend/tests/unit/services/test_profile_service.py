"""Unit tests for ProfileService."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.models.profile import MissingField
from app.models.profile import Profile
from app.models.profile import ProfileOverview
from app.services.profile_service import ProfileService
from tests.utils.profile_factory import ProfileTestDataFactory

pytestmark = pytest.mark.unit


@pytest.fixture
def service(mock_profile_repository: AsyncMock) -> ProfileService:
    """Create service instance with the mocked repository."""
    return ProfileService(profile_repository=mock_profile_repository)


# --- get_profile ---


async def test_get_profile_success(
    service: ProfileService, mock_profile_repository: AsyncMock, sample_profile_data: dict[str, Any]
) -> None:
    mock_profile_repository.get.return_value = sample_profile_data

    result = await service.get_profile("test-profile-abc123")

    assert isinstance(result, Profile)
    assert result.personal_info.full_name == "Jane Doe"
    assert result.projects[0].duration_months == 6
    mock_profile_repository.get.assert_called_once_with("test-profile-abc123")


async def test_get_profile_lists_every_empty_mandatory_field(
    service: ProfileService, mock_profile_repository: AsyncMock
) -> None:
    mock_profile_repository.get.return_value = ProfileTestDataFactory.create_document(
        "p1", personal_info={"first_name": "Jane", "last_name": "Doe"}, projects=[{"id": "x", "title": "Migration"}]
    )

    result = await service.get_profile("p1")

    assert result is not None
    assert result.missing_fields == [
        MissingField(section="personal_info", field="title"),
        MissingField(section="projects", item_id="x", field="role"),
        MissingField(section="projects", item_id="x", field="start_date"),
    ]
    assert result.projects[0].duration_months is None


async def test_get_profile_not_found(service: ProfileService, mock_profile_repository: AsyncMock) -> None:
    mock_profile_repository.get.return_value = None

    assert await service.get_profile("nonexistent") is None


# --- list_profiles ---


async def test_list_profiles_reduces_each_document_to_an_overview(
    service: ProfileService, mock_profile_repository: AsyncMock
) -> None:
    documents = [ProfileTestDataFactory.create_document(f"p{i}") for i in range(5)]
    documents[1]["personal_info"] = {"first_name": "Max", "last_name": "Muster"}  # title not filled in yet
    mock_profile_repository.query.return_value = documents

    overviews, total_count = await service.list_profiles(limit=2, offset=0)

    assert total_count == 5
    assert overviews[0] == ProfileOverview(id="p0", first_name="Jane", last_name="Doe", title="Software Engineer")
    assert overviews[1] == ProfileOverview(id="p1", first_name="Max", last_name="Muster", incomplete=True)


async def test_list_profiles_pages_in_store_order(service: ProfileService, mock_profile_repository: AsyncMock) -> None:
    mock_profile_repository.query.return_value = [ProfileTestDataFactory.create_document(f"p{i}") for i in range(5)]

    overviews, total_count = await service.list_profiles(limit=2, offset=3)

    assert [overview.id for overview in overviews] == ["p3", "p4"]
    assert total_count == 5
