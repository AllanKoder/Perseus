"""Context repository for Perseus."""
from .block import PdocBlock
from typing import Dict

class PerseusContext:
    def __init__(self):
        self.blocks: Dict[str, PdocBlock] = {}
        self.glossary = {}

    def add_block(self, block: PdocBlock):
        self.blocks[block.id] = block
        for k, v in getattr(block, "vocabulary", {}).items():
            self.glossary[k] = v

    def to_serializable(self):
        return {
            k: v.to_dict() for k, v in self.blocks.items()
        }
