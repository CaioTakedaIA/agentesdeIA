from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"


class RowError(BaseModel):
    row_index: int
    column: str
    message: str


class ValidationReport(BaseModel):
    file_path: str
    status: ValidationStatus
    errors: list[RowError] = []
    summary: str = ""


class FixReport(BaseModel):
    original_file: str
    actions_taken: list[str] = []
    rows_repaired: int = 0
    rows_dropped: int = 0


class AnalysisResult(BaseModel):
    question: str
    answer: str
    data_sources: list[str] = []
    grounded: bool = True
