from pathlib import Path
from server.models import PaperHeader
from server.parser import parse_raw_text
from server.bank_service import save_question_to_db, save_paper_and_record_usage

BASE_DIR = Path(__file__).resolve().parent.parent

def seed_database():
    header = PaperHeader(
        class_name="Class 9th",
        subject="Social Science",
        paper_name="First Unit Test",
        month_year="AUG. 2026",
        date="2026-08-12",
        marks=40,
        time="2 Hours"
    )

    # 1. Seed Theory questions
    theory_path = BASE_DIR / "samples" / "class9-social-science-theory.txt"
    if theory_path.exists():
        with open(theory_path, "r", encoding="utf-8") as f:
            theory_paper = parse_raw_text(f.read(), header)
        paper_id = save_paper_and_record_usage(theory_paper)
        print(f"Seeded Theory questions from sample. Paper ID: {paper_id}")

    # 2. Seed MCQ questions
    mcq_path = BASE_DIR / "samples" / "class9-social-science-mcq.txt"
    if mcq_path.exists():
        with open(mcq_path, "r", encoding="utf-8") as f:
            mcq_paper = parse_raw_text(f.read(), header)
        paper_id_mcq = save_paper_and_record_usage(mcq_paper)
        print(f"Seeded MCQ questions from sample. Paper ID: {paper_id_mcq}")

if __name__ == "__main__":
    seed_database()
