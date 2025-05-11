# /src/schemas/system_io.py

from datetime import datetime
from pathlib import Path
from typing import Dict
from pydantic import BaseModel, Field, HttpUrl, RootModel, constr
from .base import HTTPMethod
from .json_types import JSON

# Define type alias for constrained string
CaseInsensitiveStr = constr(strip_whitespace=True, to_lower=True)


class OASSpecFile(BaseModel):
    """Raw OpenAPI / Swagger file as system input."""

    path: Path
    content: str


class HeaderMap(RootModel):
    """Normalised HTTP header map (case-insensitive keys)."""

    root: Dict[str, str]  # Keys are treated as case-insensitive


class HTTPResponse(BaseModel):
    """Minimal execution trace entry for dynamic analysis."""

    url: HttpUrl
    method: HTTPMethod
    status_code: int = Field(ge=100, le=599)
    headers: HeaderMap
    body: JSON
    timestamp: datetime = Field(default_factory=datetime.now)
