import logging
import time

import pandas as pd

from src.domain.models import AnalysisResult
from src.domain.ports import AnalystAgentPort, LLMPort

logger = logging.getLogger(__name__)

_ANTI_HALLUCINATION_SYSTEM = """Voce e um analista de dados senior especialista no CSV carregado pelo usuario.
O usuario esta lhe enviando dados de um CSV (ate 50 linhas na amostra).

REGRAS ABSOLUTAS (GUARDRAILS):
1. Responda EXCLUSIVAMENTE com base nas linhas informadas na secao 'Amostra de Dados' do contexto.
2. NUNCA responda perguntas fora do escopo do documento (Nao responda sobre clima, historia, programacao, etc.).
3. Se a pergunta envolver linhas que nao estao listadas ou for assunto externo, responda APENAS:
   "Nao tenho dados suficientes para responder a esta pergunta com precisao."
4. NUNCA extrapole, estime ou invente valores/nomes. Se nao estiver listado, cumpra a Regra 3.
5. Se perguntarem sobre um ID ou Nome especifico, procure na 'Amostra de Dados' antes de responder.
6. Cite os valores e dados cruzados EXATAMENTE como aparecem.
7. Responda em portugues brasileiro de forma concisa e direta."""


class AnalystAgent(AnalystAgentPort):

    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    def ask(self, df: pd.DataFrame, question: str) -> AnalysisResult:
        inicio = time.perf_counter()
        logger.info("[Agente Analista] Processando pergunta: %s", question)
        context = self._build_context(df)
        user_message = f"CONTEXTO DOS DADOS:\n{context}\n\nPERGUNTA DO USUARIO:\n{question}"
        answer = self._llm.complete(_ANTI_HALLUCINATION_SYSTEM, user_message)
        elapsed = time.perf_counter() - inicio
        logger.info(
            "[Agente Analista] Resposta gerada em %.2fs com %d caracteres.",
            elapsed, len(answer),
        )
        return AnalysisResult(
            question=question,
            answer=answer,
            data_sources=[f"{len(df)} registros de {df.shape[1]} colunas"],
            grounded=True,
        )

    @staticmethod
    def _build_context(df: pd.DataFrame) -> str:
        parts = [
            f"Shape: {df.shape[0]} linhas x {df.shape[1]} colunas",
            f"Colunas: {list(df.columns)}",
            f"\n--- Estatisticas Descritivas ---\n{df.describe(include='all').to_string()}",
            f"\n--- Amostra de Dados (Primeiras 50 Linhas) ---\n{df.head(50).to_markdown(index=False)}",
        ]
        if "category" in df.columns:
            parts.append(f"\n--- Top 20 Categorias ---\n{df['category'].value_counts().head(20).to_string()}")
        if "status" in df.columns:
            parts.append(f"\n--- Top 20 Status ---\n{df['status'].value_counts().head(20).to_string()}")
        if "value" in df.columns and pd.api.types.is_numeric_dtype(df["value"]):
            if "category" in df.columns:
                grouped = df.groupby("category")["value"].agg(["mean", "sum", "count"]).head(20)
                parts.append(f"\n--- Top 20 Valor por Categoria ---\n{grouped.to_string()}")
            if "status" in df.columns:
                grouped_s = df.groupby("status")["value"].agg(["mean", "sum", "count"]).head(20)
                parts.append(f"\n--- Top 20 Valor por Status ---\n{grouped_s.to_string()}")
        if "date" in df.columns:
            parts.append(f"\n--- Intervalo de Datas ---\nMinima: {df['date'].min()} | Maxima: {df['date'].max()}")
        return "\n".join(parts)
