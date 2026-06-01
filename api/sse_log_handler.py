import logging
import re
from typing import Any

from api.event_bus import event_bus


class SSELogHandler(logging.Handler):
    _TOKEN_PATTERN = re.compile(r"\[TOKEN_USAGE\]\s+prompt=(\d+)\s+completion=(\d+)\s+total=(\d+)")
    _TIMING_PATTERN = re.compile(r"em\s+([\d.]+)s")

    # Mapeamento PT-BR de nomes de agentes (novos prefixos)
    _AGENT_MAP = {
        "[Agente Validador]": "Agente Validador",
        "[Agente Corretor]": "Agente Corretor",
        "[Agente Analista]": "Agente Analista",
        "[Servico LLM]": "Servico LLM",
        "[Pipeline]": "Orquestrador",
        # legado (caso ainda exista)
        "[GroqService]": "Servico LLM",
        "[ValidatorAgent]": "Agente Validador",
        "[FixerAgent]": "Agente Corretor",
        "[AnalystAgent]": "Agente Analista",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord):
        try:
            raw_msg = record.getMessage()

            # Extrai e publica métricas de tokens separadamente
            token_match = self._TOKEN_PATTERN.search(raw_msg)
            if token_match:
                event_bus.publish("token_usage", {
                    "prompt_tokens": int(token_match.group(1)),
                    "completion_tokens": int(token_match.group(2)),
                    "total_tokens": int(token_match.group(3)),
                })
                return  # não logar a linha crua de tokens no terminal visual

            # Detecta nome do agente pelo prefixo PT-BR
            agent_name = "Sistema"
            for prefix, name in self._AGENT_MAP.items():
                if prefix in raw_msg:
                    agent_name = name
                    break

            # Extrai tempo se disponível na mensagem
            timing = None
            timing_match = self._TIMING_PATTERN.search(raw_msg)
            if timing_match:
                timing = f"{timing_match.group(1)}s"

            event_bus.publish("log", {
                "level": record.levelname,
                "agent": agent_name,
                "message": raw_msg,
                "timestamp": self.formatter.formatTime(record, "%H:%M:%S") if self.formatter else "",
                "duration": timing,
            })
        except Exception:
            self.handleError(record)
