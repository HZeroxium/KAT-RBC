# /src/core/parsing/__init__.py

"""OpenAPI/Swagger specification parser."""

from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml
import json
from pydantic import ValidationError

from schemas.specification import (
    ParsedSpec,
    Operation,
    OperationParameter,
    APIResponse,
    ResponseSchema,
    SchemaProperty,
    ParameterLocation,
)

from schemas.common import HTTPMethod


class OpenAPIParser:
    """
    Core implementation for parsing OpenAPI specifications into the system's schema model.
    Handles both YAML and JSON formats.
    """

    def __init__(
        self, spec_path: Optional[Path] = None, spec_content: Optional[str] = None
    ):
        """
        Initialize the parser with either a file path or content string.

        Args:
            spec_path: Path to the OpenAPI specification file
            spec_content: Raw content of the OpenAPI specification
        """
        if spec_path is None and spec_content is None:
            raise ValueError("Either spec_path or spec_content must be provided")

        self.spec_path = spec_path
        self.spec_content = spec_content
        self._raw_spec = None

    def _load_spec(self) -> Dict[str, Any]:
        """Load the raw specification from file or content string."""
        if self._raw_spec is not None:
            return self._raw_spec

        if self.spec_content:
            content = self.spec_content
        else:
            with open(self.spec_path, "r", encoding="utf-8") as f:
                content = f.read()

        try:
            # Try parsing as JSON first
            self._raw_spec = json.loads(content)
        except json.JSONDecodeError:
            # Fall back to YAML parsing
            try:
                self._raw_spec = yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse OpenAPI spec: {e}")

        return self._raw_spec

    def parse(self) -> ParsedSpec:
        """
        Parse the OpenAPI specification into the system's schema model.

        Returns:
            ParsedSpec object containing the structured representation of the API
        """
        spec = self._load_spec()

        # Extract basic info
        title = spec.get("info", {}).get("title", "Unnamed API")
        version = spec.get("info", {}).get("version", "0.0.0")

        # Parse operations
        operations = self._parse_operations(spec)

        # Parse components/schemas
        components = self._parse_components(spec)

        return ParsedSpec(
            title=title, version=version, operations=operations, components=components
        )

    def _parse_operations(self, spec: Dict[str, Any]) -> List[Operation]:
        """Extract operations from the paths section of the spec."""
        operations = []

        for path, path_item in spec.get("paths", {}).items():
            for method_name, operation_data in path_item.items():
                # Skip non-HTTP method keys
                if method_name.upper() not in [m.value for m in HTTPMethod]:
                    continue

                # Get HTTP method enum value
                try:
                    method = HTTPMethod(method_name.upper())
                except ValueError:
                    continue

                # Extract operation details
                operation_id = operation_data.get(
                    "operationId", f"{method_name}_{path}"
                )
                summary = operation_data.get("summary")
                description = operation_data.get("description")

                # Parse parameters
                parameters = self._parse_parameters(
                    operation_data.get("parameters", [])
                )

                # Parse responses
                responses = self._parse_responses(operation_data.get("responses", {}))

                operations.append(
                    Operation(
                        operation_id=operation_id,
                        path=path,
                        method=method,
                        summary=summary,
                        description=description,
                        parameters=parameters,
                        responses=responses,
                    )
                )

        return operations

    def _parse_parameters(
        self, parameters: List[Dict[str, Any]]
    ) -> List[OperationParameter]:
        """Convert OpenAPI parameters to our schema format."""
        result = []

        for param in parameters:
            try:
                param_location = ParameterLocation(param.get("in", "query"))

                result.append(
                    OperationParameter(
                        name=param["name"],
                        in_=param_location,
                        required=param.get("required", False),
                        type=param.get("schema", {}).get("type", "string"),
                        description=param.get("description"),
                    )
                )
            except (KeyError, ValidationError):
                # Skip parameters with missing required fields
                continue

        return result

    def _parse_responses(self, responses: Dict[str, Any]) -> List[APIResponse]:
        """Convert OpenAPI responses to our schema format."""
        result = []

        for status_code, response_data in responses.items():
            try:
                code = int(status_code)

                # Get schema reference if present
                schema_ref = None
                if "content" in response_data:
                    for content_type, media_type in response_data["content"].items():
                        if "schema" in media_type:
                            schema = media_type["schema"]
                            if "$ref" in schema:
                                schema_ref = schema["$ref"]

                result.append(
                    APIResponse(
                        status_code=code,
                        schema_ref=schema_ref,
                        description=response_data.get("description"),
                    )
                )
            except (ValueError, ValidationError):
                # Skip responses with invalid status codes or validation errors
                continue

        return result

    def _parse_components(self, spec: Dict[str, Any]) -> Dict[str, ResponseSchema]:
        """Extract component schemas from the spec."""
        components = {}

        for schema_name, schema_data in (
            spec.get("components", {}).get("schemas", {}).items()
        ):
            properties = {}

            for prop_name, prop_data in schema_data.get("properties", {}).items():
                properties[prop_name] = SchemaProperty(
                    name=prop_name,
                    type=prop_data.get("type", "object"),
                    description=prop_data.get("description"),
                    example=prop_data.get("example"),
                )

            components[schema_name] = ResponseSchema(
                name=schema_name, properties=properties
            )

        return components


def parse_openapi(file_path: Path, content: str) -> Dict[str, Any]:
    """
    Parse an OpenAPI specification file into a structured object.

    Args:
        file_path: Path to the OpenAPI file
        content: String content of the OpenAPI file

    Returns:
        Parsed specification as a dictionary structure
    """
    # Actual implementation would use libraries like PyYAML, prance, or openapi-spec-validator
    # to parse the YAML/JSON specification into a structured form.
    # For example:
    #
    # import yaml
    # from prance import ResolvingParser
    #
    # if file_path.suffix.lower() in ['.yaml', '.yml']:
    #     raw_spec = yaml.safe_load(content)
    # else:  # Assume JSON
    #     import json
    #     raw_spec = json.loads(content)
    #
    # # Resolve references
    # parser = ResolvingParser(spec_string=content)
    # resolved_spec = parser.specification

    raise NotImplementedError("Core OpenAPI parser not yet implemented")
