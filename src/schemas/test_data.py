# /src/schemas/test_data.py

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from .common import JSON


class TestDataItem(BaseModel):
    data: JSON = Field(
        ..., description="JSON payload to be used as input for an API operation"
    )
    expected_code: int = Field(
        ...,
        description="HTTP status code expected from the operation when this data is used",
        ge=100,
        le=599,
    )


class DataSetKind(str, Enum):
    VALID = "valid"  # Test data expected to produce successful responses
    INVALID = "invalid"  # Test data expected to produce error responses


class TestDataFile(BaseModel):
    operation_id: str = Field(
        ..., description="ID of the API operation this test data applies to"
    )
    kind: DataSetKind = Field(
        ..., description="Whether this file contains valid or invalid test cases"
    )
    items: List[TestDataItem] = Field(
        ..., description="Collection of test data items with expected response codes"
    )
    path: Path = Field(
        ..., description="Filesystem path where the test data file is stored"
    )


class GeneratedTestCode(BaseModel):
    operation_sequence_id: str = Field(
        ..., description="ID of the operation sequence this test code applies to"
    )
    language: str = Field(  # "python" | "groovy"
        ...,
        description="Programming language of the generated test code (python or groovy)",
    )
    content: str = Field(..., description="Actual source code of the generated test")


class VerifiedTestCode(GeneratedTestCode):
    verified_at: datetime = Field(
        ..., description="Timestamp when this test code was semantically verified"
    )
