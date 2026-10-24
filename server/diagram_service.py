import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageOps

from server.database import get_db_connection

DIAGRAMS_DIR = Path(__file__).resolve().parent.parent / "data" / "diagrams"

def clean_diagram_image(image_bytes: bytes, output_path: Path) -> Path:
    """
    Cleans uploaded diagram image per specs/DIAGRAM-PIPELINE.md step 1:
    - Grayscale conversion
    - Contrast enhancement (auto-contrast)
    - Saves clean black-and-white image
    """
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    import io
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to grayscale
    gray = ImageOps.grayscale(img)
    # Auto contrast
    enhanced = ImageOps.autocontrast(gray, cutoff=1)
    
    enhanced.save(str(output_path), format="PNG")
    return output_path

def save_diagram_record(
    image_bytes: bytes,
    class_name: str,
    subject: str,
    chapter: str,
    tags: str,
    kind: str = "figure"
) -> Dict[str, Any]:
    conn = get_db_connection()
    cur = conn.cursor()

    diag_id = f"diag_{uuid.uuid4().hex[:8]}"
    file_path = DIAGRAMS_DIR / f"{diag_id}.png"
    clean_diagram_image(image_bytes, file_path)

    cur.execute("""
    INSERT INTO diagrams (id, class, subject, chapter, tags, file_path, labels_json, kind)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        diag_id,
        class_name,
        subject,
        chapter,
        tags,
        str(file_path),
        json.dumps([]),
        kind
    ))

    conn.commit()
    conn.close()

    return {
        "id": diag_id,
        "class": class_name,
        "subject": subject,
        "chapter": chapter,
        "tags": tags,
        "kind": kind,
        "file_path": str(file_path)
    }

def list_diagrams(
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    tag: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()

    conditions = []
    params = []
    if class_name:
        conditions.append("class = ?")
        params.append(class_name)
    if subject:
        conditions.append("subject = ?")
        params.append(subject)
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f"%{tag}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    cur.execute(f"SELECT * FROM diagrams {where_clause} ORDER BY id DESC", params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["labels"] = json.loads(r["labels_json"]) if r["labels_json"] else []
        results.append(d)
    return results

def save_diagram_labels(diag_id: str, labels: List[Dict[str, Any]]) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE diagrams SET labels_json = ? WHERE id = ?", (json.dumps(labels), diag_id))
    conn.commit()
    conn.close()
    return True
