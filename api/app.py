import logging
import os
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.event_bus import event_bus
from api.sse_log_handler import SSELogHandler
from src.pipelines.graph import build_pipeline, PipelineState

# Attach SSE log handler
sse_logger = logging.getLogger()
sse_logger.setLevel(logging.INFO)
current_handlers = [h for h in sse_logger.handlers if isinstance(h, SSELogHandler)]
if not current_handlers:
    sse_logger.addHandler(SSELogHandler())

app = FastAPI(title="Multi-Agent CSV AI System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data_upload")
UPLOAD_DIR.mkdir(exist_ok=True)


class AskRequest(BaseModel):
    question: str


@app.get("/api/stream")
async def sse_stream():
    """Endpoint for SSE connection"""
    return StreamingResponse(event_bus.listen(), media_type="text/event-stream")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file for analysis"""
    # Limpa arquivos anteriores para garantir processamento exclusivo do novo upload
    for old_file in UPLOAD_DIR.glob("*.csv"):
        old_file.unlink()

    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    event_bus.publish("upload", {"filename": file.filename, "status": "success"})
    return {"filename": file.filename, "status": "Uploaded successful"}


@app.post("/api/pipeline/run")
async def run_pipeline():
    """Run pipeline against uploaded data"""
    files = sorted(UPLOAD_DIR.glob("*.csv"))
    if not files:
        return {"status": "error", "message": "Nenhum arquivo CSV encontrado"}
    
    files_str = [str(f) for f in files]
    
    try:
        pipeline, analyst = build_pipeline()
        app.state.analyst = analyst # Store analyst for Q&A later
        
        initial_state: PipelineState = {
            "csv_files": files_str,
            "file_entries": [],
            "clean_dataframes": [],
        }
        
        event_bus.publish("pipeline_status", {"status": "running"})
        final_state = pipeline.invoke(initial_state)
        
        # Guardar dfs limpos no estado da app
        app.state.clean_dfs = final_state.get("clean_dataframes", [])
        
        # Resumo dos relatórios para enviar ao frontend
        valid_count = sum(1 for e in final_state.get("file_entries", []) if e["report"].status.value == "valid")
        invalid_count = len(final_state.get("file_entries", [])) - valid_count
        fixed_count = sum(1 for e in final_state.get("file_entries", []) if e.get("fixed_df") is not None)
        
        payload = {
            "status": "completed",
            "files_processed": len(files),
            "valid_files": valid_count,
            "invalid_files": invalid_count,
            "fixed_files": fixed_count,
            "clean_records": sum(len(df) for df in app.state.clean_dfs) if app.state.clean_dfs else 0
        }
        event_bus.publish("pipeline_status", payload)
        
        return payload
    except Exception as e:
        event_bus.publish("pipeline_status", {"status": "error", "message": str(e)})
        return {"status": "error", "message": str(e)}


@app.post("/api/ask")
async def ask_question(req: AskRequest):
    """Ask questions to the AnalystAgent based on clean data"""
    analyst = getattr(app.state, "analyst", None)
    clean_dfs = getattr(app.state, "clean_dfs", [])
    
    if not analyst or not clean_dfs:
        return {"status": "error", "message": "Pipeline não foi executado ou nenhum dado válido."}
    
    import pandas as pd
    combined = pd.concat(clean_dfs, ignore_index=True)
    
    try:
        result = analyst.ask(combined, req.question)
        return {
            "status": "success",
            "question": result.question,
            "answer": result.answer,
            "grounded": result.grounded,
            "sources": result.data_sources
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
