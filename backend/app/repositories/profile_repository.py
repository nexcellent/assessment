"""In-memory repository implementation.

A dict of documents behind the same interface the production repository implements,
working exclusively with ``dict[str, Any]``. No Pydantic models, no UUID generation, no
business logic — those belong in the service layer.

Production stores the profiles in Cosmos DB, in a container partitioned on ``tenant_id``:
that repository stamps the tenant on every write and scopes every read to it, so neither
the services nor the models know tenants exist. This one loads the documents of a
directory at start-up and keeps every change in memory until the process ends.
"""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.core.exceptions import RepositoryError
from app.core.logging import get_logger
from app.repositories.interfaces import IProfileRepository

logger = get_logger(__name__)


class MemoryProfileRepository(IProfileRepository):
    """Low-level async CRUD operations on an in-memory document store."""

    def __init__(self, fixtures_dir: Path) -> None:
        """Load every ``*.json`` document of ``fixtures_dir``, keyed by its ``id``."""
        if not fixtures_dir.is_dir():
            raise RepositoryError("load", f"Fixture directory '{fixtures_dir}' not found")
        self._documents: dict[str, dict[str, Any]] = {}
        for path in sorted(fixtures_dir.glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            self._documents[document["id"]] = document
        logger.info("Loaded %d profile documents from %s", len(self._documents), fixtures_dir)

    # --- reads ---

    async def get(self, profile_id: str) -> dict[str, Any] | None:
        """Read a single document by ID. Returns None if not found."""
        document = self._documents.get(profile_id)
        return deepcopy(document) if document is not None else None

    async def count(self) -> int:
        """Return the total document count."""
        return len(self._documents)

    async def query(self, sql: str, parameters: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        """Return every document, in load order.

        The production repository runs ``sql`` against Cosmos DB. This store has no query
        engine, so the statement and its parameters are not interpreted: callers filter
        and sort in Python.
        """
        return [deepcopy(document) for document in self._documents.values()]

    # --- writes ---

    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a new document. Returns the created document."""
        profile_id = document["id"]
        if profile_id in self._documents:
            raise RepositoryError("create", f"Document '{profile_id}' already exists")
        self._documents[profile_id] = deepcopy(document)
        return deepcopy(document)

    async def replace(self, profile_id: str, document: dict[str, Any]) -> None:
        """Replace an existing document. Raises RepositoryError if not found."""
        if profile_id not in self._documents:
            raise RepositoryError("replace", f"Document '{profile_id}' not found")
        document["id"] = profile_id
        self._documents[profile_id] = deepcopy(document)

    async def delete(self, profile_id: str) -> None:
        """Delete a document by ID. Raises RepositoryError if not found."""
        if self._documents.pop(profile_id, None) is None:
            raise RepositoryError("delete", f"Document '{profile_id}' not found")
