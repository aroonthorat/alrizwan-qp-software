# Antigravity Start Prompt — Al-Rizwan Question Paper Software

Copy everything below the line into Antigravity (agent mode), with this folder open as the workspace.

---

You are building the **Al-Rizwan Question Paper Software**, a desktop app for Al-Rizwan English School
(Nanded, Maharashtra) that turns pasted or uploaded questions into finished question papers in the
school's fixed template, checks grammar in English, Hindi, Marathi and Urdu, and keeps a question bank
with usage history by class, subject and exam.

## Read first (source of truth)

Read every file in `specs/` fully before writing any code:

1. `specs/SOFTWARE-PLAN.md` — architecture, tech stack, flow, AI gateway, database, storage, phases
2. `specs/QUESTION-PAPER-TEMPLATE.md` — the locked paper layout (Theory 3a / MCQ 3b). Do not invent layouts.
3. `specs/QUESTION-TYPES.md` — every question type, detection keywords, bank record format
4. `specs/GRAMMAR-RULES.md` — rule engine for en / hi / mr / ur

If anything in the specs conflicts, the order above wins. If something is missing, ask me before
guessing. Never change the specs files; write questions or proposals in `docs/DECISIONS.md`.

## Hard rules

- Text sizes are locked (theory 16px, MCQ 14px). Add pages instead of shrinking text.
- Never generate or rewrite a passage, poem or story. Missing source text = flag it.
- Grammar fixes are suggestions the teacher accepts; only `AUTO` rules apply silently and are logged.
- Exported `.docx` must open correctly in **Word 2007** (including Urdu RTL and Devanagari).
- The app must work fully offline with AI turned off.
- All AI calls go through `server/ai_gateway.py` only, routed by `config/routes.json`. Use only
  current-generation models listed in the plan. Never put API keys in code or in the repo — read them
  from a local `.env` that is git-ignored.
- Local-first storage: SQLite at `data/qp.sqlite`. Sync/backup are background jobs (later phase).

## Your task now: Phase 1 only

Build Phase 1 from the plan, end to end, then stop and report:

1. Scaffold the folder structure exactly as in SOFTWARE-PLAN §7 (Tauri + React app, Python FastAPI
   server, `config/`, `data/`, `specs/` already exists).
2. **New paper form:** class, subject, exam/paper name, month-year, date, marks, time.
3. **Paste input → parser:** split pasted text into question groups and questions, detect options,
   marks and `(any N)` using the rules in QUESTION-TYPES §1. No AI in Phase 1.
4. **Validation:** marks totals must equal header marks; MCQs need exactly 4 options. Block export on
   mismatch with a clear message.
5. **Template choice:** majority MCQ → 3b, otherwise 3a.
6. **Layout + .docx export** with `python-docx`: logo in header + faint grayscale watermark, double
   border, Roll No. boxes, details table, footer line on every page, hatched placeholder boxes for
   figures/maps, page breaks only between question groups/sections. Logo file: `assets/logo.jpg`
   (I will place it there).
7. **Live A4 preview** in the app matching the export.
8. Output file names: `Class <N> <Subject> - Theory Paper.docx` / `- MCQ Paper.docx`.

## Definition of done for Phase 1

- Sample input in `samples/class9-social-science.txt` (create it from the Class 9 Social Science
  example in the template spec) produces 2 theory sheets and 2 MCQ sheets matching the template.
- Marks mismatch blocks export.
- Files open in Word without layout breaking.
- `README.md` explains how to install and run (Windows), and `docs/PROGRESS.md` lists what is done and
  what is next.

Work in small commits. Before starting, give me a short implementation plan for Phase 1 and the list
of libraries you will install, then wait for my OK.
