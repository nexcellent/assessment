"""Unit tests for MemoryProfileRepository."""

from pathlib import Path

import pytest

from app.core.exceptions import RepositoryError
from app.models.profile import Profile
from app.repositories.profile_repository import MemoryProfileRepository
from tests.utils.profile_factory import ProfileTestDataFactory

pytestmark = pytest.mark.unit

LIST_ALL = "SELECT * FROM c"


@pytest.fixture
def repository(fixtures_dir: Path) -> MemoryProfileRepository:
    """A fresh store holding the fixture documents."""
    return MemoryProfileRepository(fixtures_dir)


async def test_it_loads_every_document_of_the_directory(
    repository: MemoryProfileRepository, fixtures_dir: Path
) -> None:
    files = sorted(path.stem for path in fixtures_dir.glob("*.json"))

    documents = await repository.query(LIST_ALL)

    assert await repository.count() == len(files)
    assert [document["id"] for document in documents] == files
    # Every stored document reads as a profile: the application validates them on every read.
    assert [Profile.model_validate(document).id for document in documents] == files


async def test_reads_hand_out_copies(repository: MemoryProfileRepository) -> None:
    profile_id = (await repository.query(LIST_ALL))[0]["id"]
    document = await repository.get(profile_id)
    assert document is not None

    document["personal_info"]["first_name"] = "Changed"

    stored = await repository.get(profile_id)
    assert stored is not None and stored["personal_info"]["first_name"] != "Changed"


async def test_get_unknown_returns_none(repository: MemoryProfileRepository) -> None:
    assert await repository.get("nonexistent") is None


async def test_create_replace_delete(repository: MemoryProfileRepository) -> None:
    before = await repository.count()

    created = await repository.create(ProfileTestDataFactory.create_document("new"))
    assert created["id"] == "new" and await repository.count() == before + 1

    await repository.replace("new", ProfileTestDataFactory.create_document("new", skill_categories=[]))
    replaced = await repository.get("new")
    assert replaced is not None and replaced["skill_categories"] == []

    await repository.delete("new")
    assert await repository.get("new") is None


async def test_writes_against_the_wrong_id_are_reported(repository: MemoryProfileRepository) -> None:
    existing = (await repository.query(LIST_ALL))[0]["id"]

    with pytest.raises(RepositoryError):
        await repository.create({"id": existing})
    with pytest.raises(RepositoryError):
        await repository.replace("nonexistent", {"id": "nonexistent"})
    with pytest.raises(RepositoryError):
        await repository.delete("nonexistent")


def test_a_missing_directory_is_reported(tmp_path: Path) -> None:
    with pytest.raises(RepositoryError):
        MemoryProfileRepository(tmp_path / "missing")
