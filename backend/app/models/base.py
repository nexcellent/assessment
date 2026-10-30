"""Base models and common types."""

from typing import ClassVar
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BaseEntity(BaseModel):
    """Base class for all entities with common configuration."""

    model_config = ConfigDict(
        # Pydantic v2 configuration
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=False,
    )

    # The fields an entry needs before it counts as complete. They are typed optional so
    # that a CV import can store whatever the CV gives; every other write has to fill
    # them (``require_complete`` in ``app/services``), and the profile lists what is still
    # missing (``Profile.missing_fields``).
    MANDATORY: ClassVar[tuple[str, ...]] = ()

    def missing_mandatory(self) -> list[str]:
        """The mandatory fields that are still empty, in declaration order."""
        return [name for name in self.MANDATORY if getattr(self, name) is None]


class IdentifiedEntity(BaseEntity):
    """Base entity with UUID identification."""

    id: str | None = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier (auto-generated if not provided)",
    )
