from fastapi import FastAPI

from app.api.routes import router
from app.core.error_handling import setup_error_handlers
from app.core.logging import get_logger
from app.core.logging import setup_logging
from app.core.settings import get_settings

# Setup logging early
setup_logging()
logger = get_logger(__name__)

# Initialize settings to validate configuration
settings = get_settings()
logger.info("Starting %s in %s environment", settings.project_name, settings.environment)
logger.info("API available at %s", settings.api_base_url)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="Backend service for managing consultant profiles",
    version="1.0.0",
    debug=settings.debug,
)

# Setup global error handlers
setup_error_handlers(app)

# Include API routes
app.include_router(router, prefix=settings.api_base_url)
