"""Schema models for reference table extraction."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class RowLogic(BaseModel):
    """Machine-readable logic for a table row with numeric ranges."""

    parameter: str = Field(..., description="The input parameter (e.g., 'age', 'weight')")
    min_value: Optional[float] = Field(default=None, description="Minimum value for this row")
    max_value: Optional[float] = Field(default=None, description="Maximum value for this row")
    inclusive_min: bool = Field(default=True, description="Whether min is inclusive")
    inclusive_max: bool = Field(default=True, description="Whether max is inclusive")
    unit: str = Field(..., description="Unit of measurement")


class TableRow(BaseModel):
    """A row in a reference table."""

    key: str = Field(..., description="Row identifier or category")
    values: dict[str, str] = Field(
        default_factory=dict, description="Column name to value mapping"
    )
    row_logic: list[RowLogic] = Field(
        default_factory=list,
        description="Machine-readable ranges for row matching (e.g., Age 1-5 years)",
    )


class ReferenceTable(BaseModel):
    """LLM-generated reference table content (pure extraction, no system metadata)."""

    content_type: Literal["reference_table"]
    topic: str = Field(..., description="Clinical topic or subject")
    table_name: str = Field(..., description="Name or title of the table")
    table_purpose: str = Field(
        ..., description="What this table is used for (e.g., lookup, classification)"
    )
    lookup_keys: list[str] = Field(
        default_factory=list,
        description="Input columns used for lookup (e.g., ['Age', 'Weight'])",
    )
    output_columns: list[str] = Field(
        default_factory=list,
        description="Output columns that provide results (e.g., ['Normal Heart Rate', 'Action'])",
    )
    columns: list[str] = Field(
        default_factory=list, description="All column headers in order"
    )
    rows: list[TableRow] = Field(default_factory=list, description="Table data rows with optional row_logic")
    units: dict[str, str] = Field(
        default_factory=dict,
        description="Units for numeric columns (column_name: unit)",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Important caveats, exceptions, or usage notes",
    )
    cross_references: list[str] = Field(
        default_factory=list,
        description="Reference markers exactly as shown (e.g., '→ 19', '¹')",
    )
    source_reference: str = Field(
        default="", description="Citation or source for this table"
    )
