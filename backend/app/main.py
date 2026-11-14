"""FastAPI Application for ResearchPilot Backend."""
from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.orchestration.pipeline import ResearchPipeline
from backend.app.schemas.models import ResearchPipelineResult
from backend.app.services.markdown_exporter import generate_markdown_report

app = FastAPI(
    title="ResearchPilot API",
    description="Multi-Agent Academic Research Intelligence Platform",
    version="1.0.0",
)

# Enable CORS for React frontend (Vite default is http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
# session_id -> { "pdf_paths": List[Path], "status": str, "progress": int, "result": Optional[Dict], "error": Optional[str] }
SESSIONS: Dict[str, Dict[str, Any]] = {}

class ResearchRequest(BaseModel):
    session_id: str
    question: str

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "provider": settings.LLM_PROVIDER,
        "groq_model": settings.GROQ_MODEL,
        "ollama_model": settings.OLLAMA_MODEL,
        "sample_papers_available": len(list(settings.SAMPLE_PAPERS_DIR.glob("*.pdf"))),
    }

@app.post("/api/upload")
async def upload_papers(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
):
    """Upload one or more PDF research papers into an isolated session directory."""
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    session_dir = settings.UPLOADS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "pdf_paths": [],
            "status": "idle",
            "progress": 0,
            "status_message": "Papers uploaded. Ready for research question.",
            "result": None,
            "error": None,
        }

    saved_files = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue
        dest = session_dir / f.filename
        content = await f.read()
        dest.write_bytes(content)
        if dest not in SESSIONS[session_id]["pdf_paths"]:
            SESSIONS[session_id]["pdf_paths"].append(dest)
        saved_files.append({"filename": f.filename, "size_bytes": len(content)})

    return {
        "session_id": session_id,
        "uploaded_files": saved_files,
        "total_papers_in_session": len(SESSIONS[session_id]["pdf_paths"]),
    }

@app.post("/api/load-sample")
def load_sample_papers():
    """Load default benchmark papers into a fresh session."""
    session_id = f"sample_{str(uuid.uuid4())[:6]}"
    session_dir = settings.UPLOADS_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    sample_pdfs = list(settings.SAMPLE_PAPERS_DIR.glob("*.pdf"))
    if not sample_pdfs:
        raise HTTPException(status_code=404, detail="No sample papers found in sample_papers/ directory.")

    copied_paths = []
    paper_names = []
    for pdf in sample_pdfs:
        dest = session_dir / pdf.name
        shutil.copy2(pdf, dest)
        copied_paths.append(dest)
        paper_names.append(pdf.name)

    SESSIONS[session_id] = {
        "pdf_paths": copied_paths,
        "status": "idle",
        "progress": 0,
        "status_message": "Sample papers loaded. Ready for research question.",
        "result": None,
        "error": None,
    }

    return {
        "session_id": session_id,
        "paper_names": paper_names,
        "total_papers": len(copied_paths),
        "suggested_questions": [
            "How does community solar adoption affect household energy resilience and grid stability?",
            "What are the economic and governance barriers to low-income community solar programs?",
            "How do rural and urban distribution grids differ in handling high-penetration community solar?",
        ],
    }

def _run_pipeline_task(session_id: str, question: str):
    sess = SESSIONS[session_id]
    sess["status"] = "running"
    sess["error"] = None

    def progress_callback(msg: str, pct: int):
        sess["status_message"] = msg
        sess["progress"] = pct

    try:
        pipeline = ResearchPipeline(session_id=session_id)
        result = pipeline.run(
            question=question,
            pdf_paths=sess["pdf_paths"],
            progress_cb=progress_callback,
        )
        sess["result"] = result.model_dump()
        sess["status"] = "completed"
        sess["progress"] = 100
        sess["status_message"] = "Research complete!"
    except Exception as e:
        import traceback
        traceback.print_exc()
        sess["status"] = "error"
        sess["error"] = str(e)
        sess["status_message"] = f"Pipeline failed: {e}"

@app.post("/api/research")
def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    """Start multi-agent research pipeline in background."""
    session_id = req.session_id
    if session_id not in SESSIONS or not SESSIONS[session_id]["pdf_paths"]:
        raise HTTPException(status_code=400, detail="Session does not exist or has no uploaded papers.")

    sess = SESSIONS[session_id]
    if sess["status"] == "running":
        return {"session_id": session_id, "status": "already_running"}

    background_tasks.add_task(_run_pipeline_task, session_id, req.question)
    return {"session_id": session_id, "status": "started", "question": req.question}

@app.get("/api/session/{session_id}/status")
def get_session_status(session_id: str):
    """Poll pipeline progress."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    sess = SESSIONS[session_id]
    return {
        "session_id": session_id,
        "status": sess["status"],
        "progress": sess["progress"],
        "status_message": sess.get("status_message", ""),
        "has_result": sess["result"] is not None,
        "error": sess["error"],
    }

@app.get("/api/session/{session_id}/report")
def get_research_report(session_id: str):
    """Get the full ResearchPipelineResult for a session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    sess = SESSIONS[session_id]
    if not sess["result"]:
        raise HTTPException(status_code=400, detail="Research has not yet completed for this session.")
    return sess["result"]

@app.get("/api/session/{session_id}/export/markdown")
def export_markdown(session_id: str):
    """Download research report as formatted academic Markdown."""
    if session_id not in SESSIONS or not SESSIONS[session_id]["result"]:
        raise HTTPException(status_code=404, detail="Report not available.")
    result_obj = ResearchPipelineResult(**SESSIONS[session_id]["result"])
    md_content = generate_markdown_report(result_obj)
    return PlainTextResponse(
        content=md_content,
        headers={"Content-Disposition": f"attachment; filename=researchpilot_{session_id}.md"},
    )

@app.get("/api/session/{session_id}/export/json")
def export_json(session_id: str):
    """Download research report as JSON."""
    if session_id not in SESSIONS or not SESSIONS[session_id]["result"]:
        raise HTTPException(status_code=404, detail="Report not available.")
    json_str = json.dumps(SESSIONS[session_id]["result"], indent=2, ensure_ascii=False)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=researchpilot_{session_id}.json"},
    )
