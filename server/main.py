import os
import json
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from server.models import PaperHeader, ParseRequest, ParsedPaper, ExportRequest
from server.parser import parse_raw_text, parse_paper_parts
from server.layout import paginate_paper, get_logo_data_uri
from server.export import export_paper_to_docx, generate_export_filename
from server.database import init_db

from fastapi.staticfiles import StaticFiles

# Initialize database
init_db()

app = FastAPI(
    title="Al-Rizwan Question Paper Software Backend",
    version="1.0.0"
)

# Enable CORS for Tauri and Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
SAMPLES_DIR = BASE_DIR / "samples"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
DIST_DIR = BASE_DIR / "app" / "dist"

# Mount assets directory for school logo and watermarks
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Al-Rizwan Question Paper Software", "phase": 1}

@app.get("/api/config")
def get_config():
    school_json = CONFIG_DIR / "school.json"
    if school_json.exists():
        with open(school_json, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "Al-Rizwan English School",
        "address": "Chaitaniya Nagar Road, Nanded",
        "logo_path": "assets/logo.jpg"
    }

@app.get("/api/samples")
def list_samples():
    if not SAMPLES_DIR.exists():
        return []
    files = []
    for p in SAMPLES_DIR.glob("*.txt"):
        files.append({
            "name": p.name,
            "title": p.stem.replace("-", " ").title()
        })
    return files

@app.get("/api/samples/{filename}")
def get_sample_content(filename: str):
    sample_file = SAMPLES_DIR / filename
    if not sample_file.exists():
        raise HTTPException(status_code=404, detail="Sample not found")
    with open(sample_file, "r", encoding="utf-8") as f:
        return {"filename": filename, "content": f.read()}

@app.post("/api/parse")
def parse_paper(req: ParseRequest):
    # Check if input has multiple parts (Theory + MCQ)
    parts = parse_paper_parts(req.content, req.header)
    
    results = {}
    for key, paper in parts.items():
        if req.template_override:
            paper.template = req.template_override
        sheets = paginate_paper(paper)
        results[key] = {
            "paper": paper.model_dump(),
            "sheets": sheets,
            "logo_data_uri": get_logo_data_uri()
        }

    # If only one part, also expose it as top-level 'paper' and 'sheets'
    primary_key = "theory" if "theory" in results else list(results.keys())[0]
    primary = results[primary_key]

    return {
        "parts": results,
        "paper": primary["paper"],
        "sheets": primary["sheets"],
        "logo_data_uri": primary["logo_data_uri"]
    }

@app.post("/api/export")
def export_paper(req: ExportRequest):
    paper = req.paper

    # Hard validation check per specs: Block export on marks mismatch or MCQ options != 4
    if not paper.is_valid or paper.validation_errors:
        err_msg = "Export blocked due to validation errors:\n" + "\n".join(paper.validation_errors)
        raise HTTPException(status_code=400, detail=err_msg)

    # Perform docx generation
    docx_path = export_paper_to_docx(paper, DATA_DIR)
    filename = generate_export_filename(paper)

    if not docx_path.exists():
        raise HTTPException(status_code=500, detail="Failed to generate document")

    return FileResponse(
        path=str(docx_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# Mount frontend production build if present
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
