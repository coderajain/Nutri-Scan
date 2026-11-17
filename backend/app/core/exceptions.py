"""Custom application exceptions and safe error handlers (SEC-011)."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("nutriscan.exceptions")


class NutriScanException(Exception):
    """Base exception for NutriScan domain errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OCRProcessingException(NutriScanException):
    """Raised when OCR or image preprocessing encounters a failure."""
    def __init__(self, message: str = "Image preprocessing or text recognition failed."):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class EvidenceStorageException(NutriScanException):
    """Raised when image evidence preservation fails."""
    def __init__(self, message: str = "Failed to securely store original evidence image."):
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RuleVersionNotFoundException(NutriScanException):
    """Raised when requested regulatory rule version is missing."""
    def __init__(self, version_tag: str):
        super().__init__(f"Rule version '{version_tag}' not found or inactive.", status_code=status.HTTP_404_NOT_FOUND)


class InsufficientPermissionsException(NutriScanException):
    """Raised when standard user accesses admin-only endpoint."""
    def __init__(self, message: str = "Administrator privileges required for this action."):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers that prevent leaking stack traces or internal paths."""

    @app.exception_handler(NutriScanException)
    async def nutriscan_exception_handler(request: Request, exc: NutriScanException):
        logger.warning(f"Domain error on {request.method} {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.__class__.__name__,
                    "message": exc.message,
                }
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log internal detail on server, but return clean, safe message to client (SEC-011)
        logger.error(f"Unhandled error processing {request.method} {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "InternalServerError",
                    "message": "An unexpected server error occurred. Please contact the administrator.",
                }
            }
        )
