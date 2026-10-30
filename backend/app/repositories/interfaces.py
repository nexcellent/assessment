"""Repository interfaces for data access operations."""

from abc import ABC
from abc import abstractmethod
from typing import Any


class IProfileRepository(ABC):
    """Low-level CRUD operations on profile documents.

    Works exclusively with dict[str, Any] — no Pydantic models, no UUIDs,
    no business logic. The service layer handles all conversions.
    """

    @abstractmethod
    async def get(self, profile_id: str) -> dict[str, Any] | None:
        """Read a single document by ID. Returns None if not found."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total document count."""

    @abstractmethod
    async def query(self, sql: str, parameters: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        """Execute a parameterised SQL query and return all results."""

    @abstractmethod
    async def create(self, document: dict[str, Any]) -> dict[str, Any]:
        """Insert a new document. Returns the created document."""

    @abstractmethod
    async def replace(self, profile_id: str, document: dict[str, Any]) -> None:
        """Replace an existing document. Raises RepositoryError if not found."""

    @abstractmethod
    async def delete(self, profile_id: str) -> None:
        """Delete a document by ID. Raises RepositoryError if not found."""
