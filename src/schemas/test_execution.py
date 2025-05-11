# /src/schemas/test_execution.py

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    MATCHED = "matched"
    MISMATCHED = "mismatched"
    UNKNOWN = "unknown"


class TestOutcome(BaseModel):
    test_name: str
    status: TestStatus
    expected: Optional[str]
    actual: Optional[str]
    details: Optional[str]


class TestResults(BaseModel):
    suite_id: str
    outcomes: List[TestOutcome]
    executed_at: datetime = Field(default_factory=datetime.now)


class CoverageStats(BaseModel):
    documented_codes: List[int]
    covered_codes: List[int]
    undocumented_codes: List[int]


class CoverageReport(BaseModel):
    operation_id: str
    stats: CoverageStats
    false_positive_count: int


class DashboardArtifact(BaseModel):
    coverage_reports: List[CoverageReport]
    mismatches: List[TestOutcome]
    generated_at: datetime = Field(default_factory=datetime.now)
