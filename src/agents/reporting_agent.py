# /src/agents/reporting_agent.py

from typing import List, Optional, Dict
from .base_agent import BaseAgent, AgentInput, AgentOutput
from schemas.index import TestResults, DashboardArtifact
from tools.execution import ExperienceReinforcementTool, ReporterTool


class ReportingInput(AgentInput):
    test_results: TestResults
    save_to_path: Optional[str] = None


class ReportingOutput(AgentOutput):
    dashboard: DashboardArtifact
    refined_prompts: Dict
    updated_weights: Dict


class ReportingAgent(BaseAgent):
    """Agent responsible for generating reports and improving future runs"""

    input_class = ReportingInput

    def __init__(self):
        self.reinforcement = ExperienceReinforcementTool()
        self.reporter = ReporterTool()

    def run(self, input_data: ReportingInput) -> ReportingOutput:
        # 1. Generate dashboard reports
        reporter_input = self.reporter.input_class(results=input_data.test_results)
        reporter_output = self.reporter.run(reporter_input)

        # 2. Improve future runs via reinforcement
        reinforcement_input = self.reinforcement.input_class(
            test_results=input_data.test_results
        )
        reinforcement_output = self.reinforcement.run(reinforcement_input)

        # 3. Save reports if path specified
        if input_data.save_to_path:
            # Implementation for saving the dashboard to file
            pass

        # 4. Convert reinforcement output to expected types
        # Convert list of PromptTemplate objects to dictionary by name
        refined_prompts_dict = (
            {
                template.name: {
                    "template_text": template.template_text,
                    "version": template.version,
                }
                for template in reinforcement_output.update.refined_prompts
            }
            if reinforcement_output.update.refined_prompts
            else {}
        )

        # Ensure we have a dictionary for updated weights
        updated_weights_dict = (
            reinforcement_output.update.updated_odg_weights
            if reinforcement_output.update.updated_odg_weights is not None
            else {}
        )

        # 5. Return the results
        return ReportingOutput(
            dashboard=reporter_output.dashboard,
            refined_prompts=refined_prompts_dict,
            updated_weights=updated_weights_dict,
        )
