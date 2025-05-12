# /src/schemas/common.py

from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods supported in RESTful APIs."""

    GET = "GET"  # Retrieve a resource
    POST = "POST"  # Create a new resource
    PUT = "PUT"  # Update/replace a resource
    PATCH = "PATCH"  # Partially update a resource
    DELETE = "DELETE"  # Delete a resource
    HEAD = "HEAD"  # Retrieve headers only
    OPTIONS = "OPTIONS"  # Get supported methods/CORS


# Re-export JSON types
from .json_types import JSON, JSONPrimitive
