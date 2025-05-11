# /src/tools/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseTool(ABC, Generic[InputT, OutputT]):
    """
    Minimal common interface for all tools / agents.
    """

    @abstractmethod
    def run(self, payload: InputT) -> OutputT:  # pragma: no cover
        """
        Transform an input schema instance into an output schema instance.
        Concrete subclasses provide real logic; for demo we return mocks.
        """
        raise NotImplementedError
