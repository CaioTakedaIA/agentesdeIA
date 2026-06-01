import json
import logging
import time
from datetime import datetime

import pandas as pd

from src.config.settings import EXPECTED_COLUMNS
from src.domain.models import FixReport, ValidationReport
from src.domain.ports import FixerAgentPort, LLMPort

logger = logging.getLogger(__name__)

_COLUMN_MAP_SYSTEM = (
    "Voce e um especialista em mapeamento de esquemas de dados. "
    "Recebera colunas de um CSV com nomes incorretos e a lista de colunas esperadas. "
    "Retorne APENAS um objeto JSON valido mapeando cada coluna incorreta para a coluna esperada mais provavel. "
    "Se nao houver correspondencia razoavel, mapeie para null. "
    "Exemplo: {\"id_cliente\": \"id\", \"nome_completo\": \"name\", \"xyz\": null}. "
    "NAO inclua texto adicional. Apenas o JSON."
)


class FixerAgent(FixerAgentPort):

    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    def fix(self, raw_df: pd.DataFrame, report: ValidationReport) -> tuple[pd.DataFrame, FixReport]:
        inicio = time.perf_counter()
        logger.info("[Agente Corretor] refatorando...")
        actions: list[str] = []
        df = raw_df.copy()

        df, renamed = self._align_columns(df, report)
        actions.extend(renamed)

        df, date_actions = self._normalize_dates(df)
        actions.extend(date_actions)

        df, type_actions = self._cast_types(df)
        actions.extend(type_actions)

        df, clean_actions = self._clean_string_columns(df)
        actions.extend(clean_actions)

        initial_len = len(df)
        required = [c for c in EXPECTED_COLUMNS if c in df.columns]
        df = df.dropna(subset=required, how="all").reset_index(drop=True)
        
        # Apenas removemos as linhas se elas realmente ficaram 100% invalidas nas colunas obrigatorias apos correcao
        # Preencheremos buracos com None ao inves de valores falsos, deixando o analista saber onde falta informacao real.
        dropped = initial_len - len(df)
        if dropped > 0:
            actions.append(f"Removidas {dropped} linhas severamente corrompidas")
            logger.info("[Agente Corretor] %d linhas descartadas.", dropped)
            
        elapsed = time.perf_counter() - inicio
        logger.info("[Agente Corretor] mandando para agente valiador")

        fix_report = FixReport(
            original_file=report.file_path,
            actions_taken=actions,
            rows_repaired=len(df),
            rows_dropped=dropped,
        )
        return df, fix_report

    def _align_columns(self, df: pd.DataFrame, report: ValidationReport) -> tuple[pd.DataFrame, list[str]]:
        present = set(df.columns)
        missing = [c for c in EXPECTED_COLUMNS if c not in present]
        if not missing:
            return df, []

        extra = [c for c in present if c not in EXPECTED_COLUMNS]
        if not extra:
            return df, [f"Colunas ausentes sem correspondentes extras: {missing}"]

        logger.info("[Agente Corretor] Consultando LLM para mapear colunas: %s -> %s", extra, missing)
        sample = df[extra].head(5).to_string()
        user_msg = (
            f"Colunas esperadas ausentes: {missing}\n"
            f"Colunas extras no CSV: {extra}\n"
            f"Amostra das colunas extras:\n{sample}"
        )
        try:
            raw = self._llm.complete(_COLUMN_MAP_SYSTEM, user_msg)
            
            # Limpa possíveis blocos markdown ou espaços
            raw_clean = raw.strip()
            if raw_clean.startswith("```json"):
                raw_clean = raw_clean[7:]
            if raw_clean.startswith("```"):
                raw_clean = raw_clean[3:]
            if raw_clean.endswith("```"):
                raw_clean = raw_clean[:-3]
            raw_clean = raw_clean.strip()
            
            mapping: dict = json.loads(raw_clean)
            rename_map = {
                k: v for k, v in mapping.items() if v and k in df.columns and v in EXPECTED_COLUMNS
            }
            if rename_map:
                df = df.rename(columns=rename_map)
                logger.info("[Agente Corretor] Colunas renomeadas com sucesso: %s", rename_map)
                return df, [f"Colunas renomeadas via LLM: {rename_map}"]
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("[Agente Corretor] Mapeamento LLM falhou na leitura do JSON: %s. Raw LLM: %s", exc, raw)
        return df, ["Mapeamento de colunas nao foi possivel — estrutura mantida como estava"]

    def _normalize_dates(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        if "date" not in df.columns:
            return df, []
        logger.info("[Agente Corretor] Normalizando coluna 'date' para ISO 8601.")
        df["date"] = df["date"].apply(self._parse_date_value)
        return df, ["Coluna 'date' normalizada para ISO 8601 (YYYY-MM-DD)"]

    @staticmethod
    def _parse_date_value(value: object) -> str | None:
        if pd.isna(value):
            return None
        raw = str(value).strip().strip('"').strip("'").strip()
        if not raw:
            return None
        # Tenta formatos explícitos primeiro
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y%m%d",
                   "%d.%m.%Y", "%Y.%m.%d", "%m-%d-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        # Fallback: timestamp Unix
        try:
            return datetime.fromtimestamp(int(raw)).strftime("%Y-%m-%d")
        except (ValueError, TypeError, OSError):
            pass
        # Último recurso: pandas auto-detect (lida com formatos mistos)
        try:
            parsed = pd.to_datetime(raw, dayfirst=False, infer_datetime_format=True)
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            pass
        # Se nada funcionou, retorna um placeholder em vez de None para não descartar a linha
        return "1970-01-01"

    @staticmethod
    def _cast_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        actions: list[str] = []
        if "id" in df.columns:
            df["id"] = pd.to_numeric(df["id"], errors="coerce")
            actions.append("Coluna 'id' convertida para numerico")
        if "value" in df.columns:
            df["value"] = (
                df["value"].astype(str)
                .str.replace(r"[R$\s\"']", "", regex=True) # remove quotes and R$
                .str.replace(",", ".", regex=False)
            )
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            actions.append("Coluna 'value' convertida para float (removido aspas, R$, virgula->ponto)")
        return df, actions

    @staticmethod
    def _clean_string_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        str_cols = [c for c in ["name", "category", "status"] if c in df.columns]
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        if "status" in df.columns:
            df["status"] = df["status"].str.lower()
        return df, [f"Colunas de texto normalizadas (strip/lower): {str_cols}"]
