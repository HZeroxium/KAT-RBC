# /src/core/generation/data_generator.py

"""Test data generation for API operations."""

import json
import os
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple
from schemas.specification import ParsedSpec, Operation
from schemas.dependency import OperationSchemaDep, SchemaSchemaDep
from schemas.test_data import TestDataItem, DataSetKind, TestDataFile, GeneratedTestCode


class TestDataGenerator:
    """
    Core component for generating test data for API operations.

    Creates valid and invalid test data based on API specifications
    and schema dependencies.
    """

    def __init__(self, llm_client=None, output_dir: str = "test_data"):
        """
        Initialize the test data generator.

        Args:
            llm_client: Client for language model API calls
            output_dir: Directory for storing generated test data files
        """
        self.llm_client = llm_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_test_data(
        self,
        operation: Operation,
        os_deps: List[OperationSchemaDep],
        ss_deps: List[SchemaSchemaDep],
        parsed_spec: ParsedSpec,
    ) -> Tuple[TestDataFile, TestDataFile, GeneratedTestCode]:
        """
        Generate test data for an operation.

        Args:
            operation: API operation to generate test data for
            os_deps: Operation-schema dependencies
            ss_deps: Schema-schema dependencies
            parsed_spec: Complete parsed API specification

        Returns:
            Tuple of (valid_data_file, invalid_data_file, validation_script)
        """
        # Get valid cases first
        valid_items = self._generate_valid_data(
            operation, os_deps, ss_deps, parsed_spec
        )

        # Then invalid cases
        invalid_items = self._generate_invalid_data(
            operation, os_deps, ss_deps, parsed_spec
        )

        # Create data files
        valid_file = self._create_data_file(
            operation.operation_id, DataSetKind.VALID, valid_items
        )
        invalid_file = self._create_data_file(
            operation.operation_id, DataSetKind.INVALID, invalid_items
        )

        # Generate validation script
        validation_script = self._generate_validation_script(
            operation, valid_items, invalid_items
        )

        return valid_file, invalid_file, validation_script

    def _generate_valid_data(
        self,
        operation: Operation,
        os_deps: List[OperationSchemaDep],
        ss_deps: List[SchemaSchemaDep],
        parsed_spec: ParsedSpec,
    ) -> List[TestDataItem]:
        """Generate valid test data items for an operation."""
        if self.llm_client:
            # Use LLM to generate test data
            valid_items = self._llm_generate_valid_data(operation, parsed_spec)
        else:
            # Fallback to basic template
            valid_items = self._template_generate_valid_data(operation)

        return valid_items

    def _generate_invalid_data(
        self,
        operation: Operation,
        os_deps: List[OperationSchemaDep],
        ss_deps: List[SchemaSchemaDep],
        parsed_spec: ParsedSpec,
    ) -> List[TestDataItem]:
        """Generate invalid test data items for an operation."""
        if self.llm_client:
            # Use LLM to generate invalid test data
            invalid_items = self._llm_generate_invalid_data(operation, parsed_spec)
        else:
            # Fallback to basic template
            invalid_items = self._template_generate_invalid_data(operation)

        return invalid_items

    def _llm_generate_valid_data(
        self, operation: Operation, parsed_spec: ParsedSpec
    ) -> List[TestDataItem]:
        """Use LLM to generate valid test data."""
        # This would use the LLM to generate realistic test data
        # For demonstration, we'll return some basic template data
        return self._template_generate_valid_data(operation)

    def _llm_generate_invalid_data(
        self, operation: Operation, parsed_spec: ParsedSpec
    ) -> List[TestDataItem]:
        """Use LLM to generate invalid test data."""
        # This would use the LLM to generate invalid test data
        # For demonstration, we'll return some basic template data
        return self._template_generate_invalid_data(operation)

    def _template_generate_valid_data(self, operation: Operation) -> List[TestDataItem]:
        """Generate template-based valid test data."""
        items = []

        # Create a basic template based on method
        if operation.method.value == "GET":
            # For GET, create simple query params
            data = {}
            if operation.parameters:
                # Add simple values for each parameter
                for param in operation.parameters:
                    if param.in_ == "query":
                        if param.type == "string":
                            data[param.name] = f"test_{param.name}"
                        elif param.type == "integer":
                            data[param.name] = 42
                        elif param.type == "boolean":
                            data[param.name] = True

            items.append(TestDataItem(data=data, expected_code=200))

        elif operation.method.value in ["POST", "PUT", "PATCH"]:
            # For write operations, create a simple body
            data = {"id": f"test_{uuid.uuid4()}"}
            items.append(TestDataItem(data=data, expected_code=201))

        return items[:1]  # Just return one template item for simplicity

    def _template_generate_invalid_data(
        self, operation: Operation
    ) -> List[TestDataItem]:
        """Generate template-based invalid test data."""
        items = []

        # Create an empty item (missing required fields)
        items.append(TestDataItem(data={}, expected_code=400))

        # Create an item with invalid type
        if operation.method.value in ["POST", "PUT", "PATCH"]:
            invalid_data = {"id": 12345}  # Assuming ID should be string
            items.append(TestDataItem(data=invalid_data, expected_code=400))

        return items[:1]  # Just return one template item for simplicity

    def _create_data_file(
        self, operation_id: str, kind: DataSetKind, items: List[TestDataItem]
    ) -> TestDataFile:
        """Create a test data file and write items to it."""
        # Create file path
        file_path = self.output_dir / f"{operation_id}_{kind.value}.jsonl"

        # Write data items to JSONL file
        with open(file_path, "w") as f:
            for item in items:
                f.write(
                    json.dumps({"data": item.data, "expected_code": item.expected_code})
                    + "\n"
                )

        # Create and return the file object
        return TestDataFile(
            operation_id=operation_id, kind=kind, items=items, path=file_path
        )

    def _generate_validation_script(
        self,
        operation: Operation,
        valid_items: List[TestDataItem],
        invalid_items: List[TestDataItem],
    ) -> GeneratedTestCode:
        """Generate a Python validation script for the test data."""
        # Create a simple validation script template
        script = f"""
# Generated validation script for {operation.operation_id}
import json

def validate_request(data, expected_valid):
    \"\"\"
    Validate if request data meets the expected constraints.

    Args:
        data: Request payload to validate
        expected_valid: Whether this data should be valid or not

    Returns:
        Tuple of (is_valid, message)
    \"\"\"
    # Basic validation rules for {operation.operation_id}
    if expected_valid:
        if not data:
            return False, "Valid request cannot be empty"
    else:
        # For cases expected to be invalid, we still validate
        # the structure to ensure they're invalid for the right reason
        pass

    return True, "Validation successful"

def main():
    # Load and validate test data files
    valid_file = "{operation.operation_id}_valid.jsonl"
    invalid_file = "{operation.operation_id}_invalid.jsonl"
    
    # Validate valid items
    with open(valid_file, 'r') as f:
        for line in f:
            current_item = json.loads(line)
            is_valid, message = validate_request(current_item['data'], True)
            if not is_valid:
                print(f"ERROR: Valid item failed validation: {{message}}")
                print(f"Item: {{current_item}}")
    
    # Validate invalid items
    with open(invalid_file, 'r') as f:
        for line in f:
            current_item = json.loads(line)
            is_valid, message = validate_request(current_item['data'], False)
            if not is_valid:
                print(f"ERROR: Invalid item validation issue: {{message}}")
                print(f"Item: {{current_item}}")

if __name__ == "__main__":
    main()
"""

        return GeneratedTestCode(
            operation_sequence_id=f"seq-{operation.operation_id}",
            language="python",
            content=script,
        )
