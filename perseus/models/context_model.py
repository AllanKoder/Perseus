"""Context repository for Perseus.

Implemented as a Pydantic model to provide validation and easy
serialization while keeping the original helper methods.
"""
from typing import Dict
from pydantic import BaseModel, Field
from .block import PdocBlock


class PerseusContext(BaseModel):
    blocks: Dict[str, PdocBlock] = Field(default_factory=dict)
    glossary: Dict[str, str] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
        # keep extra fields if any future extensions add them
        extra = "allow"

    def add_block(self, block: PdocBlock):
        """Add or replace a block and merge its vocabulary into the glossary."""
        self.blocks[block.id] = block
        for k, v in getattr(block, "vocabulary", {}).items():
            self.glossary[k] = v
