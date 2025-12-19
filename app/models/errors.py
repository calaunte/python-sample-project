"""Error response models."""

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    """Individual error detail."""

    type: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: ErrorDetail

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "type": "invalid_ip",
                    "message": "Invalid IPv4 address format",
                    "field": "ip",
                }
            }
        }
    )
