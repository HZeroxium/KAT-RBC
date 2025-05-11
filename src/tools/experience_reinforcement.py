# /src/tools/experience_reinforcement.py
from .base import BaseTool
from schemas.index import (
    ReinforcementInput,
    ReinforcementOutput,
    ReinforcementUpdate,
)


class ExperienceReinforcementTool(BaseTool[ReinforcementInput, ReinforcementOutput]):
    def _generate_mock_data(self) -> ReinforcementOutput:
        """Generate mock reinforcement update."""
        update = ReinforcementUpdate(refined_prompts=[], updated_odg_weights=None)
        return ReinforcementOutput(update=update)

    def run(self, payload: ReinforcementInput) -> ReinforcementOutput:
        return self._generate_mock_data()
