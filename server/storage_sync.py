import zipfile
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"

def create_nightly_backup() -> Path:
    """
    Creates a zip backup of the data folder per specs/SOFTWARE-PLAN.md §9.
    Excludes journal and temporary files.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"alrizwan_backup_{timestamp}.zip"

    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(DATA_DIR):
            for file in files:
                if file.endswith((".docx", "-journal", ".tmp")):
                    continue
                file_full = Path(root) / file
                arcname = file_full.relative_to(DATA_DIR)
                zf.write(file_full, arcname=str(arcname))

    return zip_path
