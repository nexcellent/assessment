"""Global test configuration and fixtures."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from tests.utils.profile_factory import FIXTURES_DIR
from tests.utils.profile_factory import ProfileTestDataFactory


@pytest.fixture
def fixtures_dir() -> Path:
    """The profile documents the application loads at start-up."""
    return FIXTURES_DIR


@pytest.fixture
def sample_profile_data() -> dict[str, Any]:
    """A stored profile document, as the repository returns it."""
    return ProfileTestDataFactory.create_document("test-profile-abc123")


@pytest.fixture
def mock_profile_repository() -> AsyncMock:
    """Mock profile repository (async interface)."""
    return AsyncMock()
