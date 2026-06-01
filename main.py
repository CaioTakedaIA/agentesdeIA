import argparse
import logging
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

BANNER = """
==========================================================
  Multi-Agent CSV AI System - LangGraph + Groq
  LLM: llama-3.1-8b-instant (Groq - publica e gratuita)
  Agentes: Validador -> Fixer -> Analista
==========================================================
"""


def _collect_csv_files(data_dir: str) -> list[str]:
    path = Path(data_dir)
    if not path.exists():
        logger.error("Diretório '%s' não encontrado. Execute: python scripts/generate_csvs.py", data_dir)
        sys.exit(1)
    files = sorted(path.glob("*.csv"))
    if not files:
        logger.error("Nenhum arquivo .csv encontrado em '%s'.", data_dir)
        sys.exit(1)
    return [str(f) for f in files]


def _run_pipeline(data_dir: str) -> tuple:
    from src.pipelines.graph import build_pipeline, PipelineState

    csv_files = _collect_csv_files(data_dir)
    logger.info("Iniciando pipeline com %d arquivo(s): %s", len(csv_files), csv_files)
    pipeline, analyst = build_pipeline()
    initial_state: PipelineState = {
        "csv_files": csv_files,
        "file_entries": [],
        "clean_dataframes": [],
    }
    final_state = pipeline.invoke(initial_state)
    return final_state, analyst


def _print_pipeline_report(state: dict) -> None:
    print("\n" + "=" * 60)
    print("  RELATÓRIOS DE VALIDAÇÃO")
    print("=" * 60)
    for entry in state.get("file_entries", []):
        report = entry.get("report")
        if report:
            status_icon = "[VALID]" if report.status.value == "valid" else "[INVALID]"
            print(f"\n{status_icon} {Path(report.file_path).name}")
            print(f"   Status  : {report.status.value.upper()}")
            print(f"   Resumo  : {report.summary}")
            if report.errors:
                print(f"   Erros   : {len(report.errors)} encontrados")

    print("\n" + "=" * 60)
    print("  RELATÓRIOS DE CORREÇÃO")
    print("=" * 60)
    for entry in state.get("file_entries", []):
        fix_report = entry.get("fix_report")
        if fix_report:
            print(f"\n[FIX] {Path(fix_report.original_file).name}")
            print(f"   Linhas salvas   : {fix_report.rows_repaired}")
            print(f"   Linhas descartadas: {fix_report.rows_dropped}")
            for action in fix_report.actions_taken:
                print(f"   > {action}")

    clean = state.get("clean_dataframes", [])
    print(f"\n{'=' * 60}")
    print(f"  DADOS PRONTOS PARA ANÁLISE: {len(clean)} DataFrame(s)")
    if clean:
        total_rows = sum(len(df) for df in clean)
        print(f"  Total de registros limpos: {total_rows}")
    print("=" * 60)


def _run_ask(question: str, data_dir: str) -> None:
    state, analyst = _run_pipeline(data_dir)
    clean_dfs: list[pd.DataFrame] = state.get("clean_dataframes", [])
    if not clean_dfs:
        print("\n[WARN] Nenhum dado limpo disponivel para analise.")
        return
    combined = pd.concat(clean_dfs, ignore_index=True)
    logger.info("Analista recebeu %d registros combinados", len(combined))
    result = analyst.ask(combined, question)
    print("\n" + "=" * 60)
    print(f"  PERGUNTA : {result.question}")
    print("=" * 60)
    print(f"\n  RESPOSTA :\n  {result.answer}")
    print(f"\n  Fonte    : {', '.join(result.data_sources)}")
    print(f"  Grounded : {result.grounded}")
    print("=" * 60 + "\n")


def main() -> None:
    print(BANNER)
    parser = argparse.ArgumentParser(
        description="Multi-Agent CSV AI System — LangGraph + Groq",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "mode",
        choices=["pipeline", "ask"],
        help="'pipeline' = valida e corrige CSVs | 'ask' = faz uma pergunta sobre os dados",
    )
    parser.add_argument(
        "question",
        nargs="?",
        default="",
        help="Pergunta para o modo 'ask' (ex: 'Qual categoria tem maior valor médio?')",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Diretório contendo os arquivos CSV (padrão: data/)",
    )
    args = parser.parse_args()

    if args.mode == "pipeline":
        state, _ = _run_pipeline(args.data_dir)
        _print_pipeline_report(state)
    elif args.mode == "ask":
        if not args.question.strip():
            parser.error("Informe uma pergunta. Ex: python main.py ask 'Qual o total de registros?'")
        _run_ask(args.question, args.data_dir)


if __name__ == "__main__":
    main()
