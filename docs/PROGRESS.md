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

## Phase 3: Grammar Rule Engine & Teacher Review Workspace (COMPLETED)

### Completed Deliverables
- [x] **Multilingual Rule Engine (`server/checker/grammar_engine.py`)**:
  - Implements universal rules `U-01` to `U-12` (spacing, punctuation, 12-underscore blanks, bracket spacing, Unicode NFC).
  - English rules (`EN-01` to `EN-08`): Capitalization, standalone `I`, Wh-question `?` validation, Indian/British English spelling (color $\rightarrow$ colour, center $\rightarrow$ centre, etc.).
  - Hindi rules (`HI-01` to `HI-08`): Purna Viram `।` sentence ends, standard Devanagari forms (`गई`, `लिए`, `चाहिए`), common matra corrections (`कृपया`).
  - Marathi rules (`MR-01` to `MR-07`): Modern Marathi `.` full stops, standard spellings (`आणि`, `पाहिजे`, `काही`, `नाही`), prevents slipped Hindi words (`और` $\rightarrow$ `आणि`, `है` $\rightarrow$ `आहे`).
  - Urdu rules (`UR-01` to `UR-06`): Normalizes InPage Arabic characters to standard Urdu Unicode (ي $\rightarrow$ ی, ك $\rightarrow$ ک, ه $\rightarrow$ ہ), standard verb forms (`کیجیے`, `لیے`).
- [x] **Teacher Review Workspace (`app/src/components/TeacherReviewDrawer.jsx`)**:
  - Visual color coding: Green (silently logged AUTO fixes), Yellow (FIX / STYLE suggestions), Red (critical checks).
  - One-click Accept / Dismiss actions per question item.
  - "Accept All" batch action.
  - "Add to School Dictionary" whitelist integration (`/api/grammar/dictionary/add`).
- [x] **Automated Tests**:
  - All 19 tests across `tests/test_phase1.py`, `tests/test_phase2_bank.py`, and `tests/test_phase3_grammar.py` passing cleanly.

---

## Phase 4: Diagram Bank & Code-Drawn Figures (COMPLETED)

### Completed Deliverables
- [x] **Diagram Bank Service (`server/diagram_service.py`)**:
  - Image cleanup pipeline adhering to `specs/DIAGRAM-PIPELINE.md`: automatic grayscale, autocontrast, edge cleanup.
  - Storage in `data/diagrams/` with SQLite `diagrams` table metadata (class, subject, chapter, tags, labels).
  - API endpoints `/api/diagrams/upload` and `/api/diagrams`.
- [x] **Code-Drawn SVG Generators (`server/figures/figure_generator.py`)**:
  - Dynamic `generate_timeline_svg` for chronological question types with completion blanks.
  - Dynamic `generate_concept_map_svg` for tree/flowchart completion questions.
  - Free, offline, zero-AI vector rendering with high contrast print geometry.
  - API endpoints `/api/figures/timeline` and `/api/figures/concept-map`.
- [x] **Automated Tests**:
  - All 23 tests passing across `tests/` in $1.15\text{ s}$.

---

## Phase 5: AI Gateway, Answer Key Generator & Cost Tracking (COMPLETED)

### Completed Deliverables
- [x] **AI Gateway Architecture (`server/ai_gateway.py`)**:
  - Implements multi-model routing table (`config/routes.json` with Claude Haiku 5.5, Gemini 3.8 Flash, Claude Sonnet 5.5).
  - SHA-256 caching in `ai_cache` table (cache hits return identical results for ₹0 cost).
  - Call logger tracking `time, task, model, tokens_in, tokens_out, cost_inr, cache_hit` in `ai_log` table.
  - Monthly budget cap enforcement: pauses AI once ₹500 cap is reached and continues in offline code mode.
- [x] **Answer Key .docx Generator (`server/export/answer_key_builder.py`)**:
  - Automatically produces `Class <N> <Subject> - Answer Key.docx`.
  - OpenXML table layout with question number, type, marks, and evaluation points.
  - Export endpoint at `/api/export/answer-key` and one-click UI download button.
- [x] **Automated Tests**:
  - All 26 tests passing across `tests/` in $1.42\text{ s}$.

---

## Next Steps: Phase 6 (Photo OCR, Bilingual Papers & Auto-Tagging)
1. Photo / handwriting OCR via Gemini 3.8 Flash vision.
2. Bilingual paper generator (English $\rightleftarrows$ Urdu side-by-side or stacked).
3. Diagram auto-tagging via Gemini 3.8 Flash vision.
