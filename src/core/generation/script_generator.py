# /src/core/generation/script_generator.py

"""Test script generation based on operation sequences and constraints."""

import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from schemas.dependency import OperationSequence
from schemas.constraint import UnifiedConstraint
from schemas.test_data import TestDataFile, GeneratedTestCode


class TestScriptGenerator:
    """
    Core component for generating test scripts.

    Creates executable test scripts based on operation sequences, unified constraints,
    and available test data files.
    """

    def __init__(self, llm_client=None, output_dir: str = "test_scripts"):
        """
        Initialize the test script generator.

        Args:
            llm_client: Client for language model API calls
            output_dir: Directory for storing generated test scripts
        """
        self.llm_client = llm_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_scripts(
        self,
        operation_sequence: OperationSequence,
        constraints: List[UnifiedConstraint],
        data_files: List[TestDataFile],
        language: str = "python",
    ) -> List[GeneratedTestCode]:
        """
        Generate test scripts for an operation sequence.

        Args:
            operation_sequence: Sequence of operations to test
            constraints: Unified constraints to verify
            data_files: Test data files to use
            language: Target programming language ("python" or "groovy")

        Returns:
            List of generated test code objects
        """
        if language.lower() not in ["python", "groovy"]:
            raise ValueError("Supported languages are 'python' and 'groovy'")

        # Group data files by operation ID for easy lookup
        data_by_op = self._group_data_files(data_files)

        # Group constraints by operation (assuming constraints have operation info)
        constraints_by_op = self._group_constraints(constraints)

        # Generate tests based on language
        if language.lower() == "python":
            return self._generate_python_tests(
                operation_sequence, constraints_by_op, data_by_op
            )
        else:
            return self._generate_groovy_tests(
                operation_sequence, constraints_by_op, data_by_op
            )

    def _group_data_files(
        self, data_files: List[TestDataFile]
    ) -> Dict[str, Dict[str, TestDataFile]]:
        """Group data files by operation ID and kind."""
        result = {}

        for file in data_files:
            if file.operation_id not in result:
                result[file.operation_id] = {}

            result[file.operation_id][file.kind.value] = file

        return result

    def _group_constraints(
        self, constraints: List[UnifiedConstraint]
    ) -> Dict[str, List[UnifiedConstraint]]:
        """Group constraints by operation ID (if available)."""
        # This is a placeholder - in a real implementation we'd have a way to map
        # constraints to operations, but for now we'll assume all constraints apply to all operations
        return {"all": constraints}

    def _generate_python_tests(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> List[GeneratedTestCode]:
        """Generate Python pytest-compatible test scripts."""
        # If we have an LLM client, use it to generate more sophisticated tests
        if self.llm_client:
            return self._llm_generate_python_tests(
                operation_sequence, constraints_by_op, data_by_op
            )

        # Otherwise generate a simple template
        return [
            self._template_generate_python_test(
                operation_sequence, constraints_by_op, data_by_op
            )
        ]

    def _generate_groovy_tests(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> List[GeneratedTestCode]:
        """Generate Groovy test scripts."""
        # If we have an LLM client, use it to generate more sophisticated tests
        if self.llm_client:
            return self._llm_generate_groovy_tests(
                operation_sequence, constraints_by_op, data_by_op
            )

        # Otherwise generate a simple template
        return [
            self._template_generate_groovy_test(
                operation_sequence, constraints_by_op, data_by_op
            )
        ]

    def _llm_generate_python_tests(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> List[GeneratedTestCode]:
        """Use LLM to generate Python test scripts."""
        # In a real implementation, this would use the LLM to generate scripts
        # For now, we'll use the template approach
        return [
            self._template_generate_python_test(
                operation_sequence, constraints_by_op, data_by_op
            )
        ]

    def _llm_generate_groovy_tests(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> List[GeneratedTestCode]:
        """Use LLM to generate Groovy test scripts."""
        # In a real implementation, this would use the LLM to generate scripts
        # For now, we'll use the template approach
        return [
            self._template_generate_groovy_test(
                operation_sequence, constraints_by_op, data_by_op
            )
        ]

    def _template_generate_python_test(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> GeneratedTestCode:
        """Generate a template Python test script."""
        operations = operation_sequence.operations
        sequence_id = operation_sequence.sequence_id

        # Header part
        script = """
import pytest
import requests
import json
import os
from pathlib import Path

# Base configuration
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Shared state between tests
class TestState:
    def __init__(self):
        self.responses = {}
        self.created_resources = {}

# Initialize state for this test suite
test_state = TestState()

def make_request(method, path, data=None, params=None, headers=None):
    \"\"\"Make an HTTP request to the API.\"\"\""
    url = f\"{BASE_URL}{path}\"
    request_headers = HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    response = requests.request(
        method=method,
        url=url,
        json=data,
        params=params,
        headers=request_headers
    )
    return response

def assert_status_code(response, expected_code):
    \"\"\"Assert that the response has the expected status code.\"\"\""
    assert response.status_code == expected_code, f\"Expected {expected_code}, got {response.status_code}. Response: {response.text}\"
"""

        # Add fixture for loading test data
        script += """
# Test data loading fixtures
@pytest.fixture
def load_test_data():
    \"\"\"Load test data from JSONL files.\"\"\""
    data = {}
    data_dir = Path(__file__).parent / "data"
    
    # Try to load all available test data files
"""

        # Add data loading for each operation
        for op_id in operations:
            if op_id in data_by_op:
                script += f"""
    # Load data for {op_id}
    op_data = {{}}
    for kind in ["valid", "invalid"]:
        try:
            file_path = data_dir / f"{op_id}_{{kind}}.jsonl"
            if file_path.exists():
                op_data[kind] = []
                with open(file_path, "r") as f:
                    for line in f:
                        op_data[kind].append(json.loads(line))
        except Exception as e:
            print(f"Error loading {op_id}_{{kind}}.jsonl: {{e}}")
    
    data["{op_id}"] = op_data
"""

        script += """
    return data
"""

        # Add tests for the operation sequence
        script += f"""
class TestSequence{sequence_id.replace('-', '')}:
    \"\"\"Test sequence for operation chain: {' -> '.join(operations)}\"\"\""
    
"""

        # Add test function for each operation
        for i, op_id in enumerate(operations):
            script += f"""
    def test_{i+1:02d}_{op_id}(self, load_test_data):
        \"\"\"Test {op_id} operation\"\"\""
        # Load test data
        data = load_test_data.get("{op_id}", {{}})
        valid_data = data.get("valid", [])[0]["data"] if data.get("valid") else {{"mock": "data"}}
        
        # Make the request
        response = make_request("GET", "/{op_id}", data=valid_data)  # Method should be adjusted
        
        # Store response for subsequent tests
        test_state.responses["{op_id}"] = response
        
        # Extract any resources needed for subsequent requests
        if response.status_code < 300 and response.headers.get("Content-Type", "").startswith("application/json"):
            try:
                test_state.created_resources["{op_id}"] = response.json()
            except:
                pass
        
        # Assert expected status code
        assert_status_code(response, 200)  # Expected code should be adjusted
"""

        # Add test functions for constraints
        all_constraints = constraints_by_op.get("all", [])
        for j, constraint in enumerate(all_constraints):
            script += f"""
    def test_constraint_{j+1:02d}(self):
        \"\"\"Test constraint: {constraint.expression}\"\"\""
        # This would check if the constraint was satisfied across responses
        # Simplified implementation:
        for op_id, response in test_state.responses.items():
            if response.status_code < 300:
                # In a real implementation, we would evaluate the constraint expression
                # against the appropriate response based on operation mapping
                pass
"""

        # Create file path for the script
        file_path = self.output_dir / f"test_sequence_{sequence_id}.py"
        with open(file_path, "w") as f:
            f.write(script)

        return GeneratedTestCode(
            operation_sequence_id=sequence_id, language="python", content=script
        )

    def _template_generate_groovy_test(
        self,
        operation_sequence: OperationSequence,
        constraints_by_op: Dict[str, List[UnifiedConstraint]],
        data_by_op: Dict[str, Dict[str, TestDataFile]],
    ) -> GeneratedTestCode:
        """Generate a template Groovy test script."""
        operations = operation_sequence.operations
        sequence_id = operation_sequence.sequence_id

        # Basic Groovy script structure for REST API testing
        script = """
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

// Configuration
def baseUrl = System.getenv('API_BASE_URL') ?: 'http://localhost:8000'
def headers = [
    'Content-Type': 'application/json',
    'Accept': 'application/json'
]

// Shared state
def responses = [:]
def createdResources = [:]

// Helper functions
def makeRequest(method, path, data = null, params = null, additionalHeaders = null) {
    def url = "${baseUrl}${path}"
    def conn = new URL(url).openConnection() as HttpURLConnection
    conn.requestMethod = method
    
    // Set headers
    headers.each { key, value ->
        conn.setRequestProperty(key, value)
    }
    
    if (additionalHeaders) {
        additionalHeaders.each { key, value ->
            conn.setRequestProperty(key, value)
        }
    }
    
    // Set request parameters if provided
    if (params) {
        def queryString = params.collect { key, value -> "${key}=${URLEncoder.encode(value.toString(), 'UTF-8')}" }.join('&')
        url += "?" + queryString
    }
    
    // Write request body if provided
    if (data && (method == 'POST' || method == 'PUT' || method == 'PATCH')) {
        conn.doOutput = true
        def writer = new OutputStreamWriter(conn.outputStream)
        writer.write(JsonOutput.toJson(data))
        writer.flush()
        writer.close()
    }
    
    // Get response
    def responseCode = conn.responseCode
    def responseBody = ""
    
    if (responseCode >= 200 && responseCode < 300) {
        responseBody = conn.inputStream.text
    } else {
        responseBody = conn.errorStream ? conn.errorStream.text : ""
    }
    
    def response = [
        statusCode: responseCode,
        body: responseBody,
        headers: conn.headerFields.collectEntries { key, value -> [key, value.join('; ')] }
    ]
    
    if (responseBody && response.headers['Content-Type']?.contains('application/json')) {
        response.json = new JsonSlurper().parseText(responseBody)
    }
    
    return response
}

def assertStatusCode(response, expectedCode) {
    assert response.statusCode == expectedCode : "Expected status ${expectedCode}, got ${response.statusCode}. Response: ${response.body}"
}

// Load test data
def loadTestData() {
    def data = [:]
    def dataDir = new File('data')
    
"""

        # Add data loading for each operation
        for op_id in operations:
            if op_id in data_by_op:
                script += f"""
    // Load data for {op_id}
    data['{op_id}'] = [valid: [], invalid: []]
    ['valid', 'invalid'].each {{ kindName ->
        def file = new File(dataDir, "{op_id}_${{kindName}}.jsonl")
        if (file.exists()) {{
            file.eachLine {{ line ->
                data['{op_id}'][kindName] << new JsonSlurper().parseText(line)
            }}
        }}
    }}
"""

        script += """
    return data
}

// Begin test script
def testData = loadTestData()

println "Running test sequence..."
"""

        # Add test steps for each operation
        for i, op_id in enumerate(operations):
            script += f"""
// Step {i+1}: Test {op_id}
println "Testing operation: {op_id}"

def {op_id}Data = testData['{op_id}']?.valid?.get(0)?.data ?: [mock: "data"]
def {op_id}Response = makeRequest('GET', '/{op_id}', {op_id}Data)  // Method should be adjusted

// Store response for subsequent tests
responses['{op_id}'] = {op_id}Response

// Extract any resources needed for subsequent requests
if ({op_id}Response.statusCode < 300 && {op_id}Response.json) {{
    createdResources['{op_id}'] = {op_id}Response.json
}}

// Assert expected status code
assertStatusCode({op_id}Response, 200)  // Expected code should be adjusted
"""

        # Add constraint checks
        all_constraints = constraints_by_op.get("all", [])
        if all_constraints:
            script += """
// Check constraints
println "Checking constraints..."
"""

        for j, constraint in enumerate(all_constraints):
            script += f"""
// Constraint {j+1}: {constraint.expression}
// In a real implementation, we would evaluate the constraint expression
// against the appropriate response based on operation mapping
"""

        script += """
println "Test sequence completed successfully!"
"""

        # Create file path for the script
        file_path = self.output_dir / f"test_sequence_{sequence_id}.groovy"
        with open(file_path, "w") as f:
            f.write(script)

        return GeneratedTestCode(
            operation_sequence_id=sequence_id, language="groovy", content=script
        )
