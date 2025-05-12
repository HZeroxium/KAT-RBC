# /src/tools/base.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, Any

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseTool(ABC, Generic[InputT, OutputT]):
    """
    Base abstract class for all tools in the KAT-RBC framework.

    All tools follow the same pattern:
    1. Take a strongly-typed input payload
    2. Process it according to their specific logic
    3. Return a strongly-typed output payload

    This enables composition and chaining of tools in workflows.
    """

    @abstractmethod
    def run(self, payload: InputT) -> OutputT:  # pragma: no cover
        """
        Transform an input schema instance into an output schema instance.
        Must be implemented by concrete subclasses.

        Args:
            payload: Input data conforming to the tool's input schema

        Returns:
            Output data conforming to the tool's output schema
        """
        raise NotImplementedError

    def _use_core_logic(self, payload: InputT) -> OutputT:
        """
        Demonstrate how to integrate with core implementation logic.
        This method should be overridden by subclasses to show the integration pattern.

        Args:
            payload: Input data conforming to the tool's input schema

        Returns:
            Output data conforming to the tool's output schema
        """
        raise NotImplementedError("Core logic integration not implemented")

    def get_config(self) -> Dict[str, Any]:
        """
        Return the tool's configuration.
        Can be overridden by subclasses to provide custom configuration.

        Returns:
            A dictionary containing the tool's configuration
        """
        return {"name": self.__class__.__name__}
