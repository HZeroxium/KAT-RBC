# /src/agents/constraint_mining_agent.py

from typing import List, Optional
from .base_agent import BaseAgent, AgentInput, AgentOutput
from schemas.index import ParsedSpec
from schemas.constraint import StaticConstraint, DynamicInvariant, UnifiedConstraint
from schemas.system_io import HTTPResponse
from tools.mining import (
    StaticConstraintMinerTool,
    DynamicConstraintMinerTool,
    ConstraintCombinerTool,
)


class ConstraintMiningInput(AgentInput):
    parsed_spec: ParsedSpec
    execution_logs: Optional[List[HTTPResponse]] = None


class ConstraintMiningOutput(AgentOutput):
    unified_constraints: List[UnifiedConstraint]
    static_constraints: List[StaticConstraint]
    dynamic_invariants: List[DynamicInvariant]


class ConstraintMiningAgent(BaseAgent):
    """Agent responsible for mining constraints from API specification and execution logs"""

    input_class = ConstraintMiningInput

    def __init__(self):
        self.static_miner = StaticConstraintMinerTool()
        self.dynamic_miner = DynamicConstraintMinerTool()
        self.combiner = ConstraintCombinerTool()

    def run(self, input_data: ConstraintMiningInput) -> ConstraintMiningOutput:
        # 1. Extract static constraints from the specification
        static_input = self.static_miner.input_class(parsed_spec=input_data.parsed_spec)
        static_output = self.static_miner.run(static_input)

        # 2. Extract dynamic invariants from execution logs (if available)
        dynamic_input = self.dynamic_miner.input_class(
            execution_logs=input_data.execution_logs or []
        )
        dynamic_output = self.dynamic_miner.run(dynamic_input)

        # 3. Combine constraints
        combiner_input = self.combiner.input_class(
            static_constraints=static_output.constraints,
            invariants=dynamic_output.invariants,
        )
        combiner_output = self.combiner.run(combiner_input)

        # 4. Return combined results
        return ConstraintMiningOutput(
            unified_constraints=combiner_output.unified_constraints,
            static_constraints=static_output.constraints,
            dynamic_invariants=dynamic_output.invariants,
        )
