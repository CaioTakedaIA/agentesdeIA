import logging

import pandas as pd

from src.config.settings import EXPECTED_COLUMNS
from src.domain.models import RowError, ValidationReport, ValidationStatus
from src.domain.ports import LLMPort, ValidatorAgentPort
from src.services.csv_service import load_raw

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Voce e um validador de dados CSV. Recebe um relatorio de erros estruturado e deve gerar "
    "um resumo tecnico conciso em portugues. "
    "REGRAS ABSOLUTAS: "
    "1. Descreva APENAS os erros que estao no relatorio fornecido. "
    "2. NAO adicione informacoes ou suposicoes que nao estejam no relatorio. "
    "3. Seja objetivo e tecnico. Maximo de 3 paragrafos."
)


class ValidatorAgent(ValidatorAgentPort):

    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    def validate(self, file_path: str) -> tuple[pd.DataFrame | None, ValidationReport]:
        logger.info("[Agente Validador] Iniciando analise de: %s", file_path)
        try:
            df = load_raw(file_path)
        except Exception as exc:
            logger.error("[Agente Validador] Erro critico ao carregar '%s': %s", file_path, exc)
            report = ValidationReport(
                file_path=file_path,
                status=ValidationStatus.INVALID,
                errors=[RowError(row_index=-1, column="file", message=str(exc))],
                summary=f"Erro critico ao carregar arquivo: {exc}",
            )
            return None, report

        logger.info("[Agente Validador] Arquivo carregado: %d linhas x %d colunas", len(df), len(df.columns))
        errors = self._check_schema(df)
        status = ValidationStatus.VALID if not errors else ValidationStatus.INVALID

        if errors:
            logger.warning(
                "[Agente Validador] CSV fora de formato ou estrutura identificada. Mandando apara gente resposvel pela refatoracao."
            )
            summary = self._generate_summary(file_path, df, errors)
        else:
            logger.info(
                "[Agente Validador] Validacao concluida com sucesso — %d registros validos. Chatbot liberado.",
                len(df),
            )
            summary = f"Arquivo valido. {len(df)} registros conforme schema esperado."

        report = ValidationReport(file_path=file_path, status=status, errors=errors, summary=summary)
        return df, report

    def _check_schema(self, df: pd.DataFrame) -> list[RowError]:
        errors: list[RowError] = []
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
        for col in missing_cols:
            errors.append(RowError(row_index=-1, column=col, message=f"Coluna obrigatoria ausente: '{col}'"))

        present_cols = [c for c in EXPECTED_COLUMNS if c in df.columns]
        for idx, row in df.iterrows():
            for col in present_cols:
                val = row[col]
                if pd.isna(val) or str(val).strip() == "":
                    errors.append(RowError(row_index=int(str(idx)), column=col, message="Valor ausente ou vazio"))
            if len(errors) >= 150:
                break
                
        if "value" in df.columns:
            try:
                pd.to_numeric(df["value"], errors="raise")
            except Exception:
                errors.append(RowError(row_index=-1, column="value", message="Valores nao numericos detectados"))
        if "date" in df.columns:
            try:
                pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")
            except Exception:
                errors.append(RowError(row_index=-1, column="date", message="Datas fora do padrao ISO"))
                
        return errors

    def _generate_summary(self, file_path: str, df: pd.DataFrame, errors: list[RowError]) -> str:
        error_lines = "\n".join(
            f"  Linha {e.row_index}, coluna '{e.column}': {e.message}" for e in errors[:25]
        )
        suffix = f"\n  ... e mais {len(errors) - 25} erros." if len(errors) > 25 else ""
        user_msg = (
            f"Arquivo: {file_path}\n"
            f"Dimensoes: {df.shape[0]} linhas x {df.shape[1]} colunas\n"
            f"Colunas encontradas: {list(df.columns)}\n"
            f"Colunas esperadas: {EXPECTED_COLUMNS}\n"
            f"Total de erros: {len(errors)}\n"
            f"Erros encontrados:\n{error_lines}{suffix}"
        )
        return self._llm.complete(_SYSTEM_PROMPT, user_msg)
