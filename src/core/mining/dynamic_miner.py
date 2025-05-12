# /src/core/mining/dynamic_miner.py

"""Dynamic invariant mining from API execution logs."""

import re
import uuid
import collections
from typing import Dict, List, Set, Any
from schemas.system_io import HTTPResponse
from schemas.constraint import DynamicInvariant


class DynamicInvariantMiner:
    """
    Core component for mining dynamic invariants from API execution logs.

    Uses an approach inspired by Daikon to infer likely invariants
    from observed API responses.
    """

    def discover_invariants(
        self, execution_logs: List[HTTPResponse]
    ) -> List[DynamicInvariant]:
        """
        Discover dynamic invariants from API execution logs.

        Args:
            execution_logs: List of recorded API responses

        Returns:
            List of discovered dynamic invariants
        """
        if not execution_logs:
            return []

        # Group logs by endpoint-method combination
        grouped_logs = self._group_logs(execution_logs)

        invariants = []

        # Process each endpoint-method group
        for endpoint_method, logs in grouped_logs.items():
            endpoint_invariants = self._discover_endpoint_invariants(logs)
            invariants.extend(endpoint_invariants)

        return invariants

    def _group_logs(self, logs: List[HTTPResponse]) -> Dict[str, List[HTTPResponse]]:
        """Group logs by endpoint-method combination."""
        grouped = collections.defaultdict(list)

        for log in logs:
            # Extract endpoint from URL path
            url_parts = log.url.path.split("/")

            # Simple heuristic to identify endpoint pattern - would be more sophisticated in real impl
            endpoint = "/".join([""] + url_parts[1:3])  # e.g., /v1/charges

            key = f"{endpoint}:{log.method.value}"
            grouped[key].append(log)

        return grouped

    def _discover_endpoint_invariants(
        self, logs: List[HTTPResponse]
    ) -> List[DynamicInvariant]:
        """Discover invariants for a specific endpoint-method combination."""
        if not logs:
            return []

        invariants = []

        # Extract response properties
        properties = self._extract_response_properties(logs)

        # Look for numeric properties
        numeric_props = self._identify_numeric_properties(logs, properties)

        # Check for range invariants
        for prop in numeric_props:
            range_invariants = self._check_range_invariants(logs, prop)
            invariants.extend(range_invariants)

        # Check for size invariants for arrays
        array_props = self._identify_array_properties(logs, properties)
        for prop in array_props:
            size_invariants = self._check_size_invariants(logs, prop)
            invariants.extend(size_invariants)

        return invariants

    def _extract_response_properties(self, logs: List[HTTPResponse]) -> Set[str]:
        """Extract all response properties from logs."""
        properties = set()

        for log in logs:
            flat_props = self._flatten_json(log.body)
            properties.update(flat_props)

        return properties

    def _flatten_json(self, json_obj, prefix="") -> Set[str]:
        """Flatten a nested JSON object into dot-notation properties."""
        properties = set()

        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    properties.update(self._flatten_json(value, new_prefix))
                else:
                    properties.add(new_prefix)
        elif isinstance(json_obj, list) and json_obj:
            # Only process first item in arrays to get structure
            if json_obj and isinstance(json_obj[0], (dict, list)):
                array_props = self._flatten_json(json_obj[0], prefix)
                properties.update(array_props)
            else:
                properties.add(f"{prefix}[]")

        return properties

    def _identify_numeric_properties(
        self, logs: List[HTTPResponse], properties: Set[str]
    ) -> Set[str]:
        """Identify properties that always contain numeric values."""
        numeric_props = set(properties)

        for prop in properties:
            for log in logs:
                value = self._get_nested_value(log.body, prop)
                if value is None or not isinstance(value, (int, float)):
                    # Remove non-numeric properties
                    if prop in numeric_props:
                        numeric_props.remove(prop)
                    break

        return numeric_props

    def _identify_array_properties(
        self, logs: List[HTTPResponse], properties: Set[str]
    ) -> Set[str]:
        """Identify properties that always contain arrays."""
        array_props = set()

        for prop in properties:
            is_array = True
            for log in logs:
                value = self._get_nested_value(log.body, prop)
                if not isinstance(value, list):
                    is_array = False
                    break

            if is_array:
                array_props.add(prop)

        return array_props

    def _get_nested_value(self, json_obj, property_path):
        """Get a value from a nested JSON object using dot notation."""
        parts = property_path.split(".")
        current = json_obj

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _check_range_invariants(
        self, logs: List[HTTPResponse], property_path: str
    ) -> List[DynamicInvariant]:
        """Check for range invariants on numeric properties."""
        invariants = []
        values = []

        # Collect values
        for log in logs:
            value = self._get_nested_value(log.body, property_path)
            if value is not None:
                values.append(value)

        if not values:
            return []

        # Check for non-negative
        if all(v >= 0 for v in values):
            invariants.append(
                DynamicInvariant(
                    id=f"dynamic-{uuid.uuid4()}",
                    variables=[f"response.{property_path}"],
                    expression=f"response.{property_path} >= 0",
                )
            )

        return invariants

    def _check_size_invariants(
        self, logs: List[HTTPResponse], property_path: str
    ) -> List[DynamicInvariant]:
        """Check for size invariants on array properties."""
        invariants = []

        # Check if size is always non-negative (trivial but demonstrates concept)
        invariants.append(
            DynamicInvariant(
                id=f"dynamic-{uuid.uuid4()}",
                variables=[f"size(response.{property_path})"],
                expression=f"size(response.{property_path}) >= 0",
            )
        )

        return invariants


class DaikonInvariantMiner:
    """
    Core implementation for mining dynamic invariants from API execution logs.

    Uses Daikon-like techniques to infer invariants from runtime data.
    """

    def extract_invariants(
        self, execution_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract invariants from API execution logs.

        Args:
            execution_logs: List of API execution logs/responses

        Returns:
            List of extracted invariants
        """
        # This would implement AGORA/Daikon invariant detection:
        # 1. Flatten and normalize the execution logs
        # 2. Generate trace files in Daikon format
        # 3. Run Daikon to infer likely invariants
        # 4. Convert Daikon output to our schema

        raise NotImplementedError("Dynamic invariant mining not yet implemented")
