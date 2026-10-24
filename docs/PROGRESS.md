# Progress — Al-Rizwan Question Paper Software

## Phase 1: Core Layout Engine & Question Paper Generation

### Completed
- [x] Initialized Git repository and configured `.gitignore`.
- [x] Scaffolding: `config/school.json`, `config/routes.json`, `data/dictionary/`, `specs/`.
- [x] Installed Python dependencies: `fastapi`, `uvicorn`, `python-docx`, `pydantic`, `pytest`, `lxml`, `pillow`.

### In Progress
- [ ] Backend modules: `parser/`, `checker/`, `layout/`, `export/`, `figures/`, `ai_gateway.py`.
- [ ] Rule-based parser for groups, questions, options, marks, and diagrams.
- [ ] Validation: marks totals, MCQ 4 options, export blocking.
- [ ] Template 3a (Theory) and 3b (MCQ) layout & docx generator.
- [ ] React UI: New paper form, paste workspace, live A4 preview, docx export download.
- [ ] Reference sample: `samples/class9-social-science.txt` (2 sheets Theory, 2 sheets MCQ).

### Next Phases
- Phase 2: Question bank + usage history + auto-pick.
- Phase 3: Rule engine + LanguageTool + review screen.
- Phase 4: Diagram bank + label tool + code-drawn SVG tables/timelines/concept maps.
- Phase 5: AI gateway (parse fallback, Hindi/Marathi/Urdu grammar, answer key).
- Phase 6: OCR from photos, bilingual papers, diagram auto-tagging.
- Phase 7: Multi-branch sync (Supabase), roles, cost dashboard.
