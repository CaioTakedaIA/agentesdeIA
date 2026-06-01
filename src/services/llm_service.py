import logging
import time

from groq import Groq

from src.config.settings import settings
from src.domain.ports import LLMPort

logger = logging.getLogger(__name__)


class GroqService(LLMPort):
    def __init__(self) -> None:
        self._client = Groq(api_key=settings.groq_api_key)
        self._model = settings.groq_model
        logger.info(
            "[Servico LLM] Conectado ao modelo %s via Groq API (console.groq.com)",
            self._model,
        )

    def complete(self, system: str, user: str) -> str:
        inicio = time.perf_counter()
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            max_tokens=2048,
        )
        elapsed = time.perf_counter() - inicio

        usage = response.usage
        if usage:
            logger.info(
                "[Servico LLM] Resposta em %.2fs | Tokens: entrada=%d saida=%d total=%d",
                elapsed,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )
            logger.info(
                "[TOKEN_USAGE] prompt=%d completion=%d total=%d",
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )

        return response.choices[0].message.content.strip()
