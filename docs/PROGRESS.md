# Progress — Al-Rizwan Question Paper Software

## Phase 1: Core Layout Engine & Question Paper Generation (COMPLETED)

### Completed Deliverables
- [x] Initialized Git repository and configured defensive `.gitignore`.
- [x] Scaffolding: `app/` (Tauri + React + Vite + Tailwind CSS), `server/` (FastAPI), `config/`, `data/`, `specs/`.
- [x] Installed and configured dependencies: `fastapi`, `uvicorn`, `python-docx`, `pydantic`, `pillow`, `lxml`, `pytest`.
- [x] **New Paper Form**: Class, Subject, Paper Title, Month-Year, Date, Marks, Time, Roll No. boxes.
- [x] **Deterministic Rule Parser** (`server/parser/rule_parser.py`):
  - Question group headings (`Q.1)`, `Q.2)`...).
  - Marks detection: `(10 × 1 = 10)`, `(5 × 2 = 10)`, `(3 + 3 = 6)`, `(any N)`.
  - Option detection and normalization into standard `(1)`, `(2)`, `(3)`, `(4)`.
  - Detection of diagram, figure, and outline map keywords.
  - Multi-part paper detection (Theory + MCQ combined inputs).
- [x] **Validation Engine**:
  - Marks sum matching header marks.
  - MCQ option count validation (strictly 4 options).
  - Hard export block on mismatch with error messages.
- [x] **Template Selection**:
  - Majority MCQ $\rightarrow$ Template 3b; otherwise Template 3a.
- [x] **Locked A4 Live Preview**:
  - 794px width (A4 @ 96dpi), 12mm margins, `4px double #1a1a1a` border inset.
  - 7% opacity grayscale watermark behind content.
  - Masthead with school name, address, exam title in caps, 4 Roll No. boxes.
  - Header details table.
  - Theory locked 16px text / line-height 1.8, 17.5px bold headings, hatched figure (`280×175px`) and map (`560×620px`) boxes.
  - MCQ locked 14px text / line-height 1.5, instructions box, 2-column layout with vertical rule, continuous 1–N numbering, rough work box.
  - Outer margin footer on every sheet with `Page n of N`.
- [x] **Word 2007 Compatible .docx Export** (`server/export/docx_builder.py`):
  - Inset double page borders (`w:pgBorders`).
  - Faint grayscale watermark in header (`assets/logo_watermark.png`).
  - Multi-column section for MCQ with vertical rule.
  - Dynamic page numbering footer fields (`PAGE` / `NUMPAGES`).
  - Strict naming convention: `Class <N> <Subject> - Theory Paper.docx` / `- MCQ Paper.docx`.
- [x] **Reference Sample Verification**:
  - `samples/class9-social-science.txt` produces 2 Theory sheets and 2 MCQ sheets matching the reference specifications.
- [x] **Automated Tests**:
  - All 8 tests in `tests/test_phase1.py` passing cleanly in $< 1$ second.

---

## Next Steps: Phase 2 (Question Bank & History)
1. Complete SQLite question bank integration with `questions`, `papers`, `paper_items`, `usage` tables.
2. Filter bank by class, subject, chapter, type, marks, language.
3. Track question usage history by exam and date.
4. Repetition detection: Warn when a question was used in the same class/subject within the last 2 exams.
5. Auto-pick questions based on blueprint and least-recently-used history.
