# /src/schemas/json_types.py

"""Module for properly defining JSON type structures to avoid recursion issues."""

from typing import Dict, List, Union, TypeAlias, Any

# Define JSON primitives
JSONPrimitive = Union[str, int, float, bool, None]

# First define with Any to avoid recursion issues
JSON_Base: TypeAlias = Union[JSONPrimitive, List[Any], Dict[str, Any]]

# Then create the proper recursive type using TypeAlias
JSON: TypeAlias = Union[JSONPrimitive, List[JSON_Base], Dict[str, JSON_Base]]

# This avoids the infinite recursion during schema generation
# while still providing the correct type information
