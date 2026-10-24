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

## Phase 2: Question Bank, History & Blueprint Auto-Pick (COMPLETED)

### Completed Deliverables
- [x] **Question Bank Storage & Service (`server/bank_service.py`)**:
  - Full CRUD operations with SQLite `questions`, `papers`, `paper_items`, `usage` tables.
  - Seeding script [`server/seed_bank.py`](file:///e:/Codespace/alrizwan-qp-software/server/seed_bank.py) populated with 67 realistic questions.
- [x] **Question Bank Explorer UI (`app/src/components/QuestionBankModal.jsx`)**:
  - Instant search across text, keywords, and chapters.
  - Multi-criteria filtering by Class, Subject, Question Type, and Marks.
  - Question cards with colored badges and historical exam usage tags (`Used in First Unit Test (2026-08-12)` / `Fresh (Never used)`).
  - One-click "Insert into Paper" button.
- [x] **Repetition Guardrail (`specs/QUESTION-TYPES.md §8`)**:
  - Automatically checks each question against SQLite usage history.
  - Flags and warns if a question was used in the same class and subject within the last 2 exams.
  - Prevents internal duplicate questions within the same paper.
- [x] **Blueprint Auto-Pick Paper Builder (`app/src/components/AutoPickModal.jsx`)**:
  - Generates full papers by question count and template type.
  - Applies **least-recently-used** algorithm to ensure freshness and balance across chapters.
  - Auto-updates the live A4 preview and header marks.
- [x] **Glass & Liquid Morphism UI Design System**:
  - Ambient fluid liquid gradient meshes.
  - Translucent frosted glass surfaces (`glass-card`, `glass-input`, `glass-button-primary`).
  - Subtle light reflections and responsive hover micro-interactions.
  - Strictly preserves locked A4 print/export geometries for the paper canvas.
- [x] **Automated Tests**:
  - All 13 tests across `tests/test_phase1.py` and `tests/test_phase2_bank.py` passing in $1.06\text{ s}$.

---

## Next Steps: Phase 3 (Grammar Rule Engine, LanguageTool & Side-by-Side Review)
1. Complete rule engine for Hindi, Marathi, and Urdu wording checks.
2. Integrate self-hosted LanguageTool for English (`en-GB`).
3. TipTap / ProseMirror rich-text side-by-side review screen with colored suggestion marks.
4. One-click Accept / Reject workflow and custom school dictionary.
