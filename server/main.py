import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from server.figures import generate_timeline_svg, generate_concept_map_svg
from server.diagram_service import save_diagram_record, list_diagrams, save_diagram_labels
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from server.models import PaperHeader, ParseRequest, ParsedPaper, ExportRequest
from server.parser import parse_raw_text, parse_paper_parts
from server.layout import paginate_paper, get_logo_data_uri
from server.export import export_paper_to_docx, generate_export_filename, build_answer_key_docx
from server.ai_gateway import ai_gateway
from server.ai_client import ai_client
from server.storage_sync import (
    create_nightly_backup,
    get_sync_status,
    flush_queue_to_worker,
    queue_sync_action
)
from server.bilingual_service import translate_paper_to_bilingual, build_bilingual_docx
from server.database import init_db, get_db_connection
from server.bank_service import (
    list_bank_questions,
    save_paper_and_record_usage,
    check_paper_repetition_warnings,
    auto_pick_from_bank
)
from server.checker import audit_paper_grammar, check_question_grammar

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
        # Repetition check from SQLite history
        rep_warns = check_paper_repetition_warnings(paper)
        paper.validation_warnings.extend(rep_warns)

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

@app.get("/api/bank/questions")
def get_bank_questions(
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    chapter: Optional[str] = None,
    q_type: Optional[str] = None,
    lang: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    return list_bank_questions(
        class_filter=class_name,
        subject_filter=subject,
        chapter_filter=chapter,
        type_filter=q_type,
        lang_filter=lang,
        search_query=q,
        limit=limit,
        offset=offset
    )

class AutoPickRequest(BaseModel):
    header: PaperHeader
    template: str = "3a"
    question_count: int = 10
    preferred_type: Optional[str] = None

@app.post("/api/bank/auto-pick")
def auto_pick_paper(req: AutoPickRequest):
    try:
        paper = auto_pick_from_bank(
            header=req.header,
            template=req.template,
            question_count=req.question_count,
            preferred_type=req.preferred_type
        )
        sheets = paginate_paper(paper)
        return {
            "paper": paper.model_dump(),
            "sheets": sheets,
            "logo_data_uri": get_logo_data_uri()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class GrammarCheckRequest(BaseModel):
    paper: ParsedPaper

@app.post("/api/grammar/check")
def check_grammar(req: GrammarCheckRequest):
    audit_res = audit_paper_grammar(req.paper)
    sheets = paginate_paper(req.paper)
    return {
        "paper": req.paper.model_dump(),
        "sheets": sheets,
        "auto_logs": audit_res["auto_logs"],
        "suggestions": audit_res["suggestions"],
        "total_auto_fixed": audit_res["total_auto_fixed"],
        "total_suggestions": audit_res["total_suggestions"]
    }

class DictionaryAddRequest(BaseModel):
    lang: str = "en"
    word: str

@app.post("/api/grammar/dictionary/add")
def add_to_dictionary(req: DictionaryAddRequest):
    dict_dir = BASE_DIR / "data" / "dictionary"
    dict_dir.mkdir(parents=True, exist_ok=True)
    dict_file = dict_dir / f"{req.lang}.txt"
    word_clean = req.word.strip()
    with open(dict_file, "a", encoding="utf-8") as f:
        f.write(f"\n{word_clean}")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO dictionary (lang, word) VALUES (?, ?)", (req.lang, word_clean))
    conn.commit()
    conn.close()

    return {"status": "ok", "word": word_clean, "lang": req.lang}

@app.post("/api/diagrams/upload")
async def upload_diagram(
    file: UploadFile = File(...),
    class_name: str = Form("Class 9th"),
    subject: str = Form("Social Science"),
    chapter: str = Form("General"),
    tags: str = Form(""),
    kind: str = Form("figure")
):
    content = await file.read()
    record = save_diagram_record(content, class_name, subject, chapter, tags, kind)
    return record

@app.get("/api/diagrams")
def get_diagrams(
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    tag: Optional[str] = None
):
    return list_diagrams(class_name, subject, tag)

class TimelineRequest(BaseModel):
    events: List[Dict[str, Any]]
    width: int = 560
    height: int = 140

@app.post("/api/figures/timeline")
def create_timeline(req: TimelineRequest):
    svg = generate_timeline_svg(req.events, req.width, req.height)
    return Response(content=svg, media_type="image/svg+xml")

class ConceptMapRequest(BaseModel):
    root_title: str
    branches: List[Dict[str, Any]]
    width: int = 560
    height: int = 180

@app.post("/api/figures/concept-map")
def create_concept_map(req: ConceptMapRequest):
    svg = generate_concept_map_svg(req.root_title, req.branches, req.width, req.height)
    return Response(content=svg, media_type="image/svg+xml")

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

    # Record paper and question usage in SQLite
    try:
        save_paper_and_record_usage(paper, str(docx_path))
    except Exception as err:
        print(f"Warning: Failed to record paper usage in SQLite: {err}")

    return FileResponse(
        path=str(docx_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.post("/api/export/answer-key")
def export_answer_key(req: ExportRequest):
    paper = req.paper
    res = ai_gateway.call(task="answer_key", payload={"paper": paper.model_dump()})
    answers_data = res.get("answers", [])

    cls_clean = paper.header.class_name.strip()
    if not cls_clean.lower().startswith("class"):
        cls_clean = f"Class {cls_clean}"
    filename = f"{cls_clean} {paper.header.subject.strip()} - Answer Key.docx"
    out_path = DATA_DIR / filename

    build_answer_key_docx(paper, answers_data, out_path)
    return FileResponse(
        path=str(out_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.post("/api/backup/create")
def make_backup():
    zip_path = create_nightly_backup()
    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip"
    )

@app.post("/api/ocr/upload")
async def ocr_upload(file: UploadFile = File(...)):
    content = await file.read()
    b64_img = base64.b64encode(content).decode("utf-8")
    res = ai_client.call(
        task="ocr_page",
        payload={"image_base64": b64_img, "mime_type": file.content_type or "image/jpeg"}
    )
    return {"text": res.get("text", "")}

@app.post("/api/bilingual/translate")
def translate_bilingual(req: ExportRequest):
    paper_dict = req.paper.model_dump()
    bilingual = translate_paper_to_bilingual(paper_dict)
    return {"bilingual_paper": bilingual}

@app.post("/api/export/bilingual")
def export_bilingual(req: ExportRequest):
    paper_dict = req.paper.model_dump()
    bilingual = translate_paper_to_bilingual(paper_dict)
    out_path = build_bilingual_docx(bilingual)
    return FileResponse(
        path=str(out_path),
        filename=out_path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

class AutoTagRequest(BaseModel):
    filename: str
    subject: Optional[str] = "Science"
    chapter: Optional[str] = "General"
    image_base64: Optional[str] = None

@app.post("/api/diagrams/auto-tag")
def auto_tag_diagram(req: AutoTagRequest):
    res = ai_client.call(
        task="diagram_tag",
        payload={
            "filename": req.filename,
            "subject": req.subject,
            "chapter": req.chapter,
            "image_base64": req.image_base64
        }
    )
    return res

@app.get("/api/sync/status")
def sync_status():
    return get_sync_status()

@app.post("/api/sync/flush")
def sync_flush():
    return flush_queue_to_worker()

@app.get("/api/admin/ai-stats")
def get_ai_stats():
    return ai_gateway.get_stats()

class BudgetCapRequest(BaseModel):
    monthly_cap: float

@app.post("/api/admin/set-budget-cap")
def set_budget_cap(req: BudgetCapRequest):
    ai_gateway.set_monthly_cap(req.monthly_cap)
    return {"status": "updated", "monthly_cap": req.monthly_cap}

@app.get("/api/admin/dictionary")
def get_dictionary():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT lang, word FROM dictionary ORDER BY lang, word")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"dictionary": rows}

class DictDeleteRequest(BaseModel):
    word: str
    lang: str

@app.delete("/api/admin/dictionary")
def remove_from_dictionary(req: DictDeleteRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM dictionary WHERE lang = ? AND word = ?", (req.lang, req.word))
    conn.commit()
    conn.close()

    dict_file = BASE_DIR / "data" / "dictionary" / f"{req.lang}.txt"
    if dict_file.exists():
        with open(dict_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and l.strip() != req.word]
        with open(dict_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return {"status": "removed"}

# Mount frontend production build if present
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)
