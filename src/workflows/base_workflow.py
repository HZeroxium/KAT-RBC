# /src/workflows/base_workflow.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class WorkflowInput(BaseModel):
    """Base class for workflow inputs"""

    pass


class WorkflowOutput(BaseModel):
    """Base class for workflow outputs"""

    pass


class BaseWorkflow(ABC):
    """Base workflow that all other workflows will inherit from"""

    @abstractmethod
    def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Execute the workflow's main functionality"""
        pass

    def __call__(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Allow the workflow to be called like a function"""
        return self.run(input_data)
