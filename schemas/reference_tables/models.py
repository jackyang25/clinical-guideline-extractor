"""Schema models for reference table extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TableRow(BaseModel):
    """A row in a reference table."""

    key: str = Field(..., description="Row identifier or category")
    values: dict[str, str] = Field(
        default_factory=dict, description="Column name to value mapping"
    )


class ReferenceTable(BaseModel):
    """LLM-generated reference table content (pure extraction, no system metadata)."""

    content_type: Literal["reference_table"]
    topic: str = Field(..., description="Clinical topic or subject")
    table_name: str = Field(..., description="Name or title of the table")
    table_purpose: str = Field(
        ..., description="What this table is used for (e.g., lookup, classification)"
    )
    columns: list[str] = Field(
        default_factory=list, description="Column headers in order"
    )
    rows: list[TableRow] = Field(default_factory=list, description="Table data rows")
    units: dict[str, str] = Field(
        default_factory=dict,
        description="Units for numeric columns (column_name: unit)",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Important caveats, exceptions, or usage notes",
    )
    source_reference: str = Field(
        default="", description="Citation or source for this table"
    )
