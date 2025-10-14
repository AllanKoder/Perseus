"""Data model for a Pdoc block, implemented with Pydantic BaseModel."""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator

class PdocBlock(BaseModel):
    id: str
    watch: bool = False
    code: bool = False
    intention: str = ""
    vocabulary: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    tickets: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)
    code_snippet: str = ""

    @validator("tickets", pre=True, each_item=False)
    def normalize_tickets(cls, v):
        """Normalize tickets into a list of strings.

        Accepts:
        - list of strings
        - list of single-key mappings like `- JIRA-123: Validate...`
        - None
        """
        if v is None:
            return []
        if isinstance(v, list):
            out = []
            for item in v:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, dict):
                    # Convert dict like {"JIRA-123": "Validate..."} -> "JIRA-123: Validate..."
                    for k, val in item.items():
                        out.append(f"{k}: {val}")
                else:
                    out.append(str(item))
            return out
        # fallback to single string
        return [str(v)]

    def to_dict(self):
        # Keep compatibility with the previous to_dict structure: include 'code' key containing the snippet
        base = self.dict(exclude={})
        # move code_snippet into 'code' key for backward compatibility
        base["code"] = base.pop("code_snippet", "")
        # merge any extras stored in extra
        extra = base.pop("extra", {}) or {}
        base.update(extra)
        return base

