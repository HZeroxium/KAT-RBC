# /src/schemas/test_generation.py

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from .base import JSON


class TestDataItem(BaseModel):
    data: JSON
    expected_code: int = Field(
        ...,
        description="HTTP status code expected from the operation when this data is used",
        ge=100,
        le=599,
    )


class DataSetKind(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


class TestDataFile(BaseModel):
    operation_id: str
    kind: DataSetKind
    items: List[TestDataItem]
    path: Path


class GeneratedTestCode(BaseModel):
    operation_sequence_id: str
    language: str  # "python" | "groovy"
    content: str  # source code


class VerifiedTestCode(GeneratedTestCode):
    verified_at: datetime
