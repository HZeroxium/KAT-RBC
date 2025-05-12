# /src/schemas/experience_reinforcement.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    name: str = Field(..., description="Name of the prompt template for identification")
    template_text: str = Field(
        ..., description="The actual prompt template text with placeholders"
    )
    version: str = Field(
        ..., description="Version of this prompt template for tracking changes"
    )


class ReinforcementUpdate(BaseModel):
    refined_prompts: List[PromptTemplate] = Field(
        ..., description="Updated prompt templates based on learning from test results"
    )
    updated_odg_weights: Optional[Dict[str, float]] = Field(
        None,
        description="Updated weights for ODG edges based on test execution feedback",
    )
