# /src/schemas/test_execution.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    MATCHED = "matched"  # Test outcome matches expected result
    MISMATCHED = "mismatched"  # Test outcome differs from expected result
    UNKNOWN = "unknown"  # Test outcome cannot be determined


class TestOutcome(BaseModel):
    test_name: str = Field(..., description="Name of the test that was executed")
    status: TestStatus = Field(
        ..., description="Status of the test execution: matched, mismatched, or unknown"
    )
    expected: Optional[str] = Field(
        None, description="Expected result or condition that the test was verifying"
    )
    actual: Optional[str] = Field(
        None, description="Actual result observed during test execution"
    )
    details: Optional[str] = Field(
        None,
        description="Additional details about the test execution or failure reason",
    )


class TestResults(BaseModel):
    suite_id: str = Field(..., description="Unique identifier for the test suite")
    outcomes: List[TestOutcome] = Field(
        ..., description="List of individual test outcomes from the execution"
    )
    executed_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the tests were executed",
    )


class CoverageStats(BaseModel):
    documented_codes: List[int] = Field(
        ..., description="HTTP status codes documented in the API specification"
    )
    covered_codes: List[int] = Field(
        ..., description="HTTP status codes covered by the test suite"
    )
    undocumented_codes: List[int] = Field(
        ...,
        description="HTTP status codes returned by API but not documented in specification",
    )


class CoverageReport(BaseModel):
    operation_id: str = Field(
        ..., description="Operation identifier the coverage report applies to"
    )
    stats: CoverageStats = Field(
        ..., description="Statistics about HTTP status code coverage for the operation"
    )
    false_positive_count: int = Field(
        ..., description="Number of false positive test failures for this operation"
    )


class DashboardArtifact(BaseModel):
    coverage_reports: List[CoverageReport] = Field(
        ..., description="Coverage reports for each tested API operation"
    )
    mismatches: List[TestOutcome] = Field(
        ..., description="List of test mismatches found during execution"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when this dashboard was generated",
    )
