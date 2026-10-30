from fastapi import APIRouter

from app.api.endpoints import health
from app.api.endpoints import profile_management
from app.api.endpoints.collections import COLLECTION_ROUTES
from app.api.endpoints.collections import collection_router

# Create the main router
router = APIRouter()

# Health check (GET /health)
router.include_router(health.router)

# Include the profile management router (list, get)
router.include_router(profile_management.router, prefix="/profiles")

# The repeated sub-collections (work experience, education, projects, skill
# categories), all under /profiles/{profile_id}/...
for route in COLLECTION_ROUTES:
    router.include_router(collection_router(route), prefix="/profiles")
