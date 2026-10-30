"""Global error handling for the application."""

import traceback
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import DomainError
from app.core.exceptions import EntityNotFoundError
from app.core.exceptions import MandatoryFieldsMissingError
from app.core.exceptions import ProfileNotFoundError
from app.core.exceptions import RepositoryError
from app.core.logging import get_logger
from app.core.settings import get_settings

logger = get_logger(__name__)


class ErrorResponse:
    """Standardized error response format."""

    def __init__(
        self, error_code: str, message: str, details: dict[str, Any] | None = None, request_id: str | None = None
    ) -> None:
        """Initialize the ErrorResponse with error details."""
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.request_id = request_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response: dict[str, Any] = {"error": {"code": self.error_code, "message": self.message}}
        if self.details:
            response["error"]["details"] = self.details
        if self.request_id:
            response["request_id"] = self.request_id
        return response


def _get_request_id(request: Request) -> str:
    """Extract or generate request ID for tracing."""
    return request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]


async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """Handle domain-specific exceptions."""
    request_id = _get_request_id(request)
    logger.warning("Domain exception [%s]: %s - %s", request_id, exc.error_code, exc.message)
    error_response = ErrorResponse(exc.error_code or "DOMAIN_ERROR", exc.message, request_id=request_id)
    # Map domain exceptions to HTTP status codes
    return JSONResponse(status_code=_get_status_code_for_domain_exception(exc), content=error_response.to_dict())


async def _validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors raised inside the application.

    Invalid request bodies never reach this handler: FastAPI raises its own
    ``RequestValidationError`` for those and answers with its default 422. This one
    catches a ``ValidationError`` from a model built in code, such as a service
    constructing an entity.
    """
    request_id = _get_request_id(request)
    errors = [
        {"field": ".".join(str(x) for x in error["loc"]), "message": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    logger.warning("Validation error [%s]: %s validation errors", request_id, len(errors))
    error_response = ErrorResponse(
        "VALIDATION_ERROR", "Request validation failed", {"validation_errors": errors}, request_id=request_id
    )
    return JSONResponse(status_code=422, content=error_response.to_dict())


async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    request_id = _get_request_id(request)
    logger.warning("HTTP exception [%s]: %s - %s", request_id, exc.status_code, exc.detail)
    error_response = ErrorResponse(f"HTTP_{exc.status_code}", str(exc.detail), request_id=request_id)
    return JSONResponse(status_code=exc.status_code, content=error_response.to_dict())


async def _general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = _get_request_id(request)
    tb_str = "".join(traceback.format_tb(exc.__traceback__))
    logger.error("Unhandled exception [%s]: %s: %s\n%s", request_id, type(exc).__name__, exc, tb_str)

    # Only dev shows the exception and traceback; every other environment gets a generic message
    if get_settings().environment == "dev":
        error_message, details = f"{type(exc).__name__}: {exc!s}", {"traceback": tb_str}
    else:
        error_message, details = "An internal server error occurred", {}

    error_response = ErrorResponse("INTERNAL_SERVER_ERROR", error_message, details, request_id=request_id)
    return JSONResponse(status_code=500, content=error_response.to_dict())


def _get_status_code_for_domain_exception(exc: DomainError) -> int:
    """Map domain exception types to HTTP status codes."""
    status_code_map = {
        ProfileNotFoundError: 404,
        EntityNotFoundError: 404,
        MandatoryFieldsMissingError: 422,
        RepositoryError: 500,
    }
    return status_code_map.get(type(exc), 500)


def setup_error_handlers(app: FastAPI) -> None:
    """Register error handlers with FastAPI app."""
    app.add_exception_handler(DomainError, _domain_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, _validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, _http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _general_exception_handler)
    logger.info("Global error handlers registered")
