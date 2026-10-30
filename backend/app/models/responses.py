"""Response models for API endpoints.

Clean, direct response models without wrapper overhead.
Errors are handled via HTTP status codes + global error handlers.
"""

from datetime import UTC
from datetime import datetime

from pydantic import Field

from app.models.base import BaseEntity
from app.models.profile import Profile
from app.models.profile import ProfileOverview


class ProfileResponse(BaseEntity):
    """Response for retrieving a single profile."""

    profile: Profile = Field(..., description="The complete profile data")


class ProfileListResponse(BaseEntity):
    """Response for listing profiles."""

    profiles: list[ProfileOverview] = Field(..., description="List of profile summaries")
    count: int = Field(..., description="Number of profiles returned in this page")
    total_count: int = Field(..., description="Total number of profiles")


# How a change to one entry is reported, phrased in one place.
_PREPOSITIONS = {"added": "to", "updated": "within", "deleted": "from"}


def modification_message(action: str, entity: str, entity_id: str, profile_id: str) -> str:
    """Phrase the confirmation for one added, updated or deleted entry."""
    return f"Successfully {action} {entity} with ID {entity_id} {_PREPOSITIONS[action]} profile with ID {profile_id}"


class ProfileModificationResponse(BaseEntity):
    """Response for all profile modification operations: the profile ID and what was done."""

    profile_id: str = Field(..., min_length=1, description="Unique identifier of the profile that was modified")
    message: str = Field(..., min_length=1, description="Human-readable message describing the operation performed")


class ServiceStatus(BaseEntity):
    """Status of an individual service dependency."""

    connected: bool = Field(..., description="Whether the service is reachable")
    latency_ms: float | None = Field(None, description="Round-trip latency in milliseconds")
    error: str | None = Field(None, description="Error message if connection failed")


class HealthCheckResponse(BaseEntity):
    """Health check response with real connectivity probes."""

    status: str = Field(..., description="Overall health: healthy | unhealthy")
    environment: str = Field(..., description="Application environment (dev, uat, prd)")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Health check timestamp (UTC)")
    services: dict[str, ServiceStatus] = Field(..., description="Connectivity status for each dependency")
