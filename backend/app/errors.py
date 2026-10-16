"""
AEGIS Structured Error Handling Module
Conforms to PRD 2: E-009 Safe exception handling and structured error reporting.
Never exposes raw stack traces or internal secrets to API clients.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class ErrorResponse(BaseModel):
    """Standardized API error contract for all client responses."""
    error_code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable safe explanation of the error")
    correlation_id: str = Field(..., description="Unique request tracing ID for server logs")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Safe context-specific metadata")


class AEGISError(Exception):
    """Base exception class for all AEGIS domain errors."""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id or str(uuid.uuid4())

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            correlation_id=self.correlation_id,
            details=self.details
        )


class ValidationError(AEGISError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
        super().__init__(message, error_code="INVALID_INPUT", status_code=400, details=details, correlation_id=correlation_id)


class NotFoundError(AEGISError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", status_code=404, details=details, correlation_id=correlation_id)


class WeatherProviderError(AEGISError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
        super().__init__(message, error_code="WEATHER_PROVIDER_UNAVAILABLE", status_code=503, details=details, correlation_id=correlation_id)


class BlockchainError(AEGISError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
        super().__init__(message, error_code="BLOCKCHAIN_ERROR", status_code=502, details=details, correlation_id=correlation_id)


class EvidenceVerificationError(AEGISError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None):
        super().__init__(message, error_code="EVIDENCE_TAMPER_DETECTED", status_code=422, details=details, correlation_id=correlation_id)
