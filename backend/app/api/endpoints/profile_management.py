"""Profile management API endpoints.

Domain exceptions raised by the services (a missing profile or entry, an incomplete
entry, ...) propagate to the centralised error handlers registered in
``app/core/error_handling.py``, which map each to its status code. Endpoints handle HTTP
only; they never catch a domain exception themselves.
"""

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from app.core.container import get_profile_service_di
from app.core.exceptions import ProfileNotFoundError
from app.models.responses import ProfileListResponse
from app.models.responses import ProfileResponse
from app.services.interfaces import IProfileService

router = APIRouter(tags=["Profile Management"])


# --- READ endpoints ---


@router.get(
    "",
    response_model=ProfileListResponse,
    summary="List Profiles",
    description="""List all profiles with pagination.

Returns a lightweight ProfileOverview for each profile rather than the full document.
Use GET /profiles/{id} to retrieve the complete profile.""",
)
async def list_profiles(
    service: Annotated[IProfileService, Depends(get_profile_service_di)],
    limit: int = Query(10, ge=1, le=100, description="Maximum number of profiles to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of profiles to skip for pagination"),
) -> ProfileListResponse:
    """List profiles with pagination."""
    overviews, total_count = await service.list_profiles(limit, offset)
    return ProfileListResponse(profiles=overviews, count=len(overviews), total_count=total_count)


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Get Profile",
    description="""Get a profile by ID.

Retrieves the complete profile with every sub-collection, plus the computed fields
(full name, current position, project durations, missing fields). Returns 404 if the
profile does not exist.""",
)
async def get_profile(
    profile_id: str,
    service: Annotated[IProfileService, Depends(get_profile_service_di)],
) -> ProfileResponse:
    """Get profile by ID."""
    profile = await service.get_profile(profile_id)
    if profile is None:
        raise ProfileNotFoundError(profile_id)

    return ProfileResponse(profile=profile)
