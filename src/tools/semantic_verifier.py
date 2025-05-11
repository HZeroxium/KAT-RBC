# /src/tools/semantic_verifier.py
from datetime import datetime
from .base import BaseTool
from schemas.index import (
    SemanticVerifierInput,
    SemanticVerifierOutput,
    VerifiedTestCode,
)


class SemanticVerifierTool(BaseTool[SemanticVerifierInput, SemanticVerifierOutput]):
    def _generate_mock_data(self, generated_tests) -> SemanticVerifierOutput:
        """Generate mock verified test code."""
        verified = [
            VerifiedTestCode(**code.dict(), verified_at=datetime.utcnow())
            for code in generated_tests
        ]
        return SemanticVerifierOutput(verified_tests=verified)

    def run(self, payload: SemanticVerifierInput) -> SemanticVerifierOutput:
        return self._generate_mock_data(payload.generated_tests)
