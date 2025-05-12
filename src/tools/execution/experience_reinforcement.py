# /src/tools/execution/experience_reinforcement.py

from ..base import BaseTool
from schemas.index import (
    ReinforcementInput,
    ReinforcementOutput,
    ReinforcementUpdate,
    PromptTemplate,
)


class ExperienceReinforcementTool(BaseTool[ReinforcementInput, ReinforcementOutput]):
    """
    Tool for learning from test outcomes to improve future test generations.
    Part of KAT's reinforcement learning capability.
    """

    input_class = ReinforcementInput

    def _generate_mock_data(self) -> ReinforcementOutput:
        """Generate mock reinforcement update."""
        # Create at least one mock prompt template to avoid empty list
        mock_prompt = PromptTemplate(
            name="default_template",
            template_text="This is a default template for {{operation_id}}",
            version="1.0.0",
        )
        update = ReinforcementUpdate(
            refined_prompts=[mock_prompt],
            updated_odg_weights={},  # Use empty dict instead of None for consistency
        )
        return ReinforcementOutput(update=update)

    def run(self, payload: ReinforcementInput) -> ReinforcementOutput:
        """
        Run reinforcement learning tool to improve future test generations.

        Args:
            payload: Input containing test results to learn from

        Returns:
            Output with updated prompts and weights
        """
        # In a full implementation, this would process the test_results
        # and use them to update prompts and weights
        return self._generate_mock_data()
