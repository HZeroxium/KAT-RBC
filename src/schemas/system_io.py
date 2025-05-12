# /src/schemas/system_io.py

from datetime import datetime
from pathlib import Path
from typing import Dict
from pydantic import BaseModel, Field, HttpUrl, RootModel, constr
from .common import HTTPMethod
from .json_types import JSON

# Define type alias for constrained string
CaseInsensitiveStr = constr(strip_whitespace=True, to_lower=True)


class OASSpecFile(BaseModel):
    """Raw OpenAPI / Swagger file as system input."""

    path: Path = Field(
        ..., description="Filesystem path to the OpenAPI/Swagger specification file"
    )
    content: str = Field(
        ..., description="Raw content of the OpenAPI/Swagger specification file"
    )


class HeaderMap(RootModel):
    """Normalised HTTP header map (case-insensitive keys)."""

    root: Dict[str, str] = Field(
        ..., description="Map of HTTP headers with case-insensitive keys"
    )


class HTTPResponse(BaseModel):
    """Minimal execution trace entry for dynamic analysis."""

    url: HttpUrl = Field(
        ..., description="Full URL of the HTTP request that generated this response"
    )
    method: HTTPMethod = Field(
        ..., description="HTTP method used for the request (GET, POST, etc.)"
    )
    status_code: int = Field(
        ge=100, le=599, description="HTTP status code returned by the server"
    )
    headers: HeaderMap = Field(..., description="HTTP headers returned in the response")
    body: JSON = Field(..., description="Parsed JSON body of the response")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When this response was recorded"
    )
