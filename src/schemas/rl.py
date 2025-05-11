# /src/schemas/rl.py

from typing import Dict, List, Optional
from pydantic import BaseModel


class PromptTemplate(BaseModel):
    name: str
    template_text: str
    version: str


class ReinforcementUpdate(BaseModel):
    refined_prompts: List[PromptTemplate]
    updated_odg_weights: Optional[Dict[str, float]]  # edge_id → weight
