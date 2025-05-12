# /src/core/execution/test_executor.py

"""Test execution against live API endpoints."""

import os
import sys
import time
import json
import pytest
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from schemas.test_data import VerifiedTestCode
from schemas.test_execution import (
    TestResults,
    TestOutcome,
    TestStatus,
)


class TestExecutor:
    """
    Core component for executing verified tests against live API endpoints.

    Runs test scripts and collects outcomes, categorizing them as matched,
    mismatched, or unknown.
    """

    def __init__(self, timeout: int = 60, parallel: bool = True, max_retries: int = 2):
        """
        Initialize the test executor.

        Args:
            timeout: Maximum execution time per test in seconds
            parallel: Whether to run tests in parallel
            max_retries: Maximum number of retries for failed tests
        """
        self.timeout = timeout
        self.parallel = parallel
        self.max_retries = max_retries

    def execute_tests(
        self, verified_tests: List[VerifiedTestCode], api_base_url: str
    ) -> TestResults:
        """
        Execute verified tests against a live API.

        Args:
            verified_tests: List of verified test code to execute
            api_base_url: Base URL of the target API

        Returns:
            Test execution results
        """
        outcomes = []
        suite_id = f"suite-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Set environment variables for tests
        os.environ["API_BASE_URL"] = api_base_url

        # Execute tests based on language
        for test in verified_tests:
            if test.language.lower() == "python":
                test_outcomes = self._execute_python_test(test)
            elif test.language.lower() == "groovy":
                test_outcomes = self._execute_groovy_test(test)
            else:
                print(f"Unsupported language: {test.language}")
                continue

            outcomes.extend(test_outcomes)

        return TestResults(
            suite_id=suite_id, outcomes=outcomes, executed_at=datetime.utcnow()
        )

    def _execute_python_test(self, test: VerifiedTestCode) -> List[TestOutcome]:
        """
        Execute a Python test script.

        Args:
            test: Verified Python test code

        Returns:
            List of test outcomes
        """
        outcomes = []

        # Create a temporary directory for test execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test module file
            test_file = temp_path / "test_execution.py"
            with open(test_file, "w") as f:
                f.write(test.content)

            # Create a pytest.ini file with test result collection
            pytest_ini = temp_path / "pytest.ini"
            with open(pytest_ini, "w") as f:
                f.write(
                    """
[pytest]
junit_family=xunit2
addopts=--junitxml=results.xml
"""
                )

            # Run pytest as a subprocess to isolate execution
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-v",
                "--junitxml=results.xml",
            ]

            try:
                # Execute the tests
                proc = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    timeout=self.timeout,
                    check=False,
                    env=dict(os.environ),
                )

                # Parse test outcomes from output
                xml_path = temp_path / "results.xml"
                if xml_path.exists():
                    outcomes = self._parse_pytest_results(xml_path)
                else:
                    # If no XML was created, create a generic outcome
                    outcomes = [
                        TestOutcome(
                            test_name=f"{test.operation_sequence_id}",
                            status=(
                                TestStatus.UNKNOWN
                                if proc.returncode != 0
                                else TestStatus.MATCHED
                            ),
                            details=f"Exit code: {proc.returncode}, Output: {proc.stdout.decode()[:200]}...",
                        )
                    ]

            except subprocess.TimeoutExpired:
                outcomes = [
                    TestOutcome(
                        test_name=f"{test.operation_sequence_id}",
                        status=TestStatus.UNKNOWN,
                        details=f"Test execution timed out after {self.timeout} seconds",
                    )
                ]
            except Exception as e:
                outcomes = [
                    TestOutcome(
                        test_name=f"{test.operation_sequence_id}",
                        status=TestStatus.UNKNOWN,
                        details=f"Error during test execution: {str(e)}",
                    )
                ]

        return outcomes

    def _execute_groovy_test(self, test: VerifiedTestCode) -> List[TestOutcome]:
        """
        Execute a Groovy test script.

        Args:
            test: Verified Groovy test code

        Returns:
            List of test outcomes
        """
        # Check if Groovy is installed
        try:
            proc = subprocess.run(
                ["groovy", "--version"], capture_output=True, check=False, timeout=5
            )
            groovy_installed = proc.returncode == 0
        except:
            groovy_installed = False

        if not groovy_installed:
            return [
                TestOutcome(
                    test_name=f"{test.operation_sequence_id}",
                    status=TestStatus.UNKNOWN,
                    details="Groovy is not installed or not available in PATH",
                )
            ]

        # Create a temporary directory for test execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test script file
            test_file = temp_path / "test_execution.groovy"
            with open(test_file, "w") as f:
                f.write(test.content)

            # Create a basic JUnit XML output generator
            result_collector = temp_path / "collect_results.groovy"
            with open(result_collector, "w") as f:
                f.write(
                    """
// Simple results collector
def testResults = [:]

// Define custom asserts that collect results
def oldAssert = this.&assert
this.metaClass.static.assert = { boolean condition, String message = "" ->
    try {
        oldAssert(condition, message)
        testResults[Thread.currentThread().stackTrace[2].methodName] = [
            status: "PASSED",
            message: "Test passed"
        ]
    } catch (AssertionError e) {
        testResults[Thread.currentThread().stackTrace[2].methodName] = [
            status: "FAILED", 
            message: message ?: e.message
        ]
        throw e
    }
}

// Run script and collect results
try {
    evaluate(new File("test_execution.groovy"))
    
    // Write results to JUnit-style XML
    def writer = new StringWriter()
    def xml = new groovy.xml.MarkupBuilder(writer)
    xml.testsuite(name: "groovy-tests", tests: testResults.size(), failures: testResults.count { it.value.status == "FAILED" }, time: "0") {
        testResults.each { testName, result ->
            testcase(name: testName, classname: "GroovyTest", time: "0") {
                if (result.status == "FAILED") {
                    failure(message: result.message, type: "AssertionError")
                }
            }
        }
    }
    
    new File("results.xml").text = writer.toString()
} catch (Exception e) {
    println "Error executing test: ${e.message}"
    # Fix: Use triple single quotes for Python string containing triple-quoted Groovy string
    new File("results.xml").text = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="groovy-tests" tests="1" failures="1">
  <testcase name="execution" classname="GroovyTest">
    <failure message="${e.message}" type="${e.class.name}"/>
  </testcase>
</testsuite>'''
}
"""
                )

            # Run the test
            try:
                # Execute the test collector (which runs the test)
                cmd = ["groovy", str(result_collector)]
                proc = subprocess.run(
                    cmd,
                    cwd=temp_dir,
                    capture_output=True,
                    timeout=self.timeout,
                    check=False,
                )

                # Parse test outcomes from output
                xml_path = temp_path / "results.xml"
                if xml_path.exists():
                    outcomes = self._parse_groovy_results(xml_path)
                else:
                    # If no XML was created, create a generic outcome
                    outcomes = [
                        TestOutcome(
                            test_name=f"{test.operation_sequence_id}",
                            status=(
                                TestStatus.UNKNOWN
                                if proc.returncode != 0
                                else TestStatus.MATCHED
                            ),
                            details=f"Exit code: {proc.returncode}, Output: {proc.stdout.decode()[:200]}...",
                        )
                    ]

            except subprocess.TimeoutExpired:
                outcomes = [
                    TestOutcome(
                        test_name=f"{test.operation_sequence_id}",
                        status=TestStatus.UNKNOWN,
                        details=f"Test execution timed out after {self.timeout} seconds",
                    )
                ]
            except Exception as e:
                outcomes = [
                    TestOutcome(
                        test_name=f"{test.operation_sequence_id}",
                        status=TestStatus.UNKNOWN,
                        details=f"Error during test execution: {str(e)}",
                    )
                ]

        return outcomes

    def _parse_pytest_results(self, xml_path: Path) -> List[TestOutcome]:
        """
        Parse pytest XML results into test outcomes.

        Args:
            xml_path: Path to pytest XML results file

        Returns:
            List of test outcomes
        """
        import xml.etree.ElementTree as ET

        outcomes = []
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for testcase in root.findall(".//testcase"):
                name = testcase.get("name", "unknown")
                classname = testcase.get("classname", "")
                test_name = f"{classname}.{name}" if classname else name

                # Check for failures or errors
                failure = testcase.find("failure")
                error = testcase.find("error")
                skipped = testcase.find("skipped")

                if failure is not None:
                    message = failure.get("message", "")
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.MISMATCHED,
                            expected=failure.get("expected", ""),
                            actual=failure.get("actual", ""),
                            details=message,
                        )
                    )
                elif error is not None:
                    message = error.get("message", "")
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.UNKNOWN,
                            details=message,
                        )
                    )
                elif skipped is not None:
                    message = skipped.get("message", "")
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.UNKNOWN,
                            details=f"Test skipped: {message}",
                        )
                    )
                else:
                    # Test passed
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.MATCHED,
                            details="Test passed",
                        )
                    )
        except Exception as e:
            # If parsing fails, create a generic outcome
            outcomes.append(
                TestOutcome(
                    test_name="xml_parsing",
                    status=TestStatus.UNKNOWN,
                    details=f"Error parsing test results: {str(e)}",
                )
            )

        return outcomes

    def _parse_groovy_results(self, xml_path: Path) -> List[TestOutcome]:
        """
        Parse Groovy/JUnit XML results into test outcomes.

        Args:
            xml_path: Path to JUnit XML results file

        Returns:
            List of test outcomes
        """
        import xml.etree.ElementTree as ET

        outcomes = []
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for testcase in root.findall(".//testcase"):
                name = testcase.get("name", "unknown")
                classname = testcase.get("classname", "")
                test_name = f"{classname}.{name}" if classname else name

                # Check for failures or errors
                failure = testcase.find("failure")
                error = testcase.find("error")

                if failure is not None:
                    message = failure.get("message", "")
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.MISMATCHED,
                            details=message,
                        )
                    )
                elif error is not None:
                    message = error.get("message", "")
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.UNKNOWN,
                            details=message,
                        )
                    )
                else:
                    # Test passed
                    outcomes.append(
                        TestOutcome(
                            test_name=test_name,
                            status=TestStatus.MATCHED,
                            details="Test passed",
                        )
                    )
        except Exception as e:
            # If parsing fails, create a generic outcome
            outcomes.append(
                TestOutcome(
                    test_name="xml_parsing",
                    status=TestStatus.UNKNOWN,
                    details=f"Error parsing test results: {str(e)}",
                )
            )

        return outcomes
