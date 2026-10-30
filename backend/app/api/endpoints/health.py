"""Health check endpoint that probes the profile store."""

import time

from fastapi import APIRouter

from app.core.container import get_profile_repository
from app.core.logging import get_logger
from app.core.settings import get_settings
from app.models.responses import HealthCheckResponse
from app.models.responses import ServiceStatus

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


async def _check_profile_store() -> ServiceStatus:
    """Probe the profile store with its cheapest read, a count."""
    start = time.perf_counter()
    try:
        count = await get_profile_repository().count()
        latency = (time.perf_counter() - start) * 1000
        logger.debug("Profile store health check OK — count=%s, latency=%.1fms", count, latency)
        return ServiceStatus(connected=True, latency_ms=round(latency, 1))
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        logger.warning("Profile store health check failed: %s", exc)
        return ServiceStatus(connected=False, latency_ms=round(latency, 1), error=str(exc))


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="""Check connectivity to the service's dependencies.

Probes the profile store with a count. Returns **healthy** when it answers,
**unhealthy** otherwise.""",
)
async def health_check() -> HealthCheckResponse:
    """Probe all dependencies and return aggregated health status."""
    store_status = await _check_profile_store()
    return HealthCheckResponse(
        status="healthy" if store_status.connected else "unhealthy",
        environment=get_settings().environment,
        services={"profile_store": store_status},
    )
