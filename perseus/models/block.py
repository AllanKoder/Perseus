"""Data model for a Pdoc block, implemented with Pydantic BaseModel."""
from typing import Dict, List
from pydantic import BaseModel, Field, field_validator

class PdocBlock(BaseModel):
    # Allow extra fields so we can validate them against global config later
    model_config = {"extra": "allow"}
    id: str
    watch: bool = False
    code: bool = False
    intention: str = ""
    vocabulary: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    tickets: List[str] = Field(default_factory=list)
    tickets_enriched: List[Dict[str, str]] = Field(default_factory=list)  # Runtime enriched data
    # extras removed; additional fields should be declared in global config
    code_snippet: str = ""

    @field_validator("tickets", mode="before")
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
        # Use Pydantic v2 model_dump for serialization
        base = self.model_dump(exclude={})
        # move code_snippet into 'code' key for backward compatibility
        base["code"] = base.pop("code_snippet", "")
        # extras are validated against global config; nothing to merge here
        return base

