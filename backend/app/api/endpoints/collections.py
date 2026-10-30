"""The repeated profile sub-collections, as one router description.

Work experience, education, projects and skill categories are the same resource over
and over: replace one entry of a list on the profile. The handlers are built here from
:data:`COLLECTION_ROUTES`, one row per collection; the field lists are not restated in
the prose, because the schema the docs already render is the accurate copy.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends

from app.core.container import get_education_service_di
from app.core.container import get_project_service_di
from app.core.container import get_skill_category_service_di
from app.core.container import get_work_experience_service_di
from app.models.responses import ProfileModificationResponse
from app.models.responses import modification_message
from app.services import entity_collection_service as collections
from app.services.entity_collection_service import CollectionSpec
from app.services.entity_collection_service import EntityCollectionService


@dataclass(frozen=True)
class CollectionRoute:
    """One sub-collection as it is addressed over HTTP."""

    spec: CollectionSpec[Any]
    segment: str
    tag: str
    noun: str
    dependency: Callable[[], EntityCollectionService[Any]]


COLLECTION_ROUTES: tuple[CollectionRoute, ...] = (
    CollectionRoute(
        collections.WORK_EXPERIENCE,
        "work-experience",
        "Work Experience",
        "Work Experience",
        get_work_experience_service_di,
    ),
    CollectionRoute(collections.EDUCATION, "education", "Education", "Education", get_education_service_di),
    CollectionRoute(collections.PROJECTS, "projects", "Projects", "Project", get_project_service_di),
    CollectionRoute(
        collections.SKILL_CATEGORIES,
        "skill-categories",
        "Skills",
        "Skill Category",
        get_skill_category_service_di,
    ),
)


def collection_router(route: CollectionRoute) -> APIRouter:
    """Build the update route for one sub-collection.

    The handler's annotations are read at definition time, so the model bound to the
    request body is the collection's own — FastAPI validates against it exactly as if
    the module named it in source.
    """
    router = APIRouter(tags=[route.tag])
    label = route.spec.label
    model = route.spec.model
    service_type = Annotated[EntityCollectionService[Any], Depends(route.dependency)]
    entry_path = f"/{{profile_id}}/{route.segment}/{{item_id}}"

    @router.put(
        entry_path,
        response_model=ProfileModificationResponse,
        summary=f"Update {route.noun}",
        description=(
            f"Replace a {label} entry.\n\n"
            f"The entry keeps its ID; every other value is taken from the request body.\n\n"
            f"Returns 404 if the profile or the entry does not exist, 422 if a mandatory field is empty."
        ),
    )
    async def update(
        profile_id: str,
        item_id: str,
        service: service_type,
        item: model = Body(..., description=f"The {label} entry to store in its place"),  # type: ignore[valid-type]
    ) -> ProfileModificationResponse:
        stored_id = await service.update(profile_id, item_id, item)
        return ProfileModificationResponse(
            profile_id=profile_id,
            message=modification_message("updated", label, stored_id, profile_id),
        )

    return router
