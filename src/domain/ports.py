from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from src.domain.models import AnalysisResult, FixReport, ValidationReport


class LLMPort(ABC):
    @abstractmethod
    def complete(self, system: str, user: str) -> str: ...


class ValidatorAgentPort(ABC):
    @abstractmethod
    def validate(self, file_path: str) -> tuple[pd.DataFrame | None, ValidationReport]: ...


class FixerAgentPort(ABC):
    @abstractmethod
    def fix(
        self, raw_df: pd.DataFrame, report: ValidationReport
    ) -> tuple[pd.DataFrame, FixReport]: ...


class AnalystAgentPort(ABC):
    @abstractmethod
    def ask(self, df: pd.DataFrame, question: str) -> AnalysisResult: ...
