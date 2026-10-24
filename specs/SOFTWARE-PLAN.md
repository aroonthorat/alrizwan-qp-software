# Al-Rizwan Question Paper Software — Build Plan

Companion files (read these with this plan):
- `QUESTION-PAPER-TEMPLATE.md` — locked paper layout (Theory 3a / MCQ 3b)
- `QUESTION-TYPES.md` — all question types, detection, bank record
- `GRAMMAR-RULES.md` — grammar & spelling rules (en / hi / mr / ur)
- `DIAGRAM-PIPELINE.md` — diagram tagging and redraw models
- `STORAGE-AND-RAG.md` — Cloudflare D1 / R2 / Workers / Vectorize, backups, RAG

**Design principle:** code does everything it can for free; AI is called only where code can't
decide, always through one gateway, on the cheapest model that does the job, with results cached.
The software must still work fully **offline without AI** (manual entry, bank, layout, export).

---

## 1. Tech stack

| Layer | Tool | Why |
|---|---|---|
| Desktop app UI | **Tauri + React** (or Electron + React) | PageMaker-style workspace with palettes, runs on school PCs, small install |
| Editor | TipTap (ProseMirror) | Rich text, Devanagari + Urdu RTL, inline suggestion marks |
| Local backend | **Python FastAPI** (runs inside the app) | Local docx export, layout, rule engine (no keys, no data) |
| Database | **Cloudflare D1** (cloud SQLite) + local SQLite offline queue | School PC not trusted with data; see `STORAGE-AND-RAG.md` |
| Files | **Cloudflare R2** | Diagrams, logo, .docx; no egress fees |
| API server | **Cloudflare Workers** | Login, AI gateway, API keys as secrets |
| RAG | **Cloudflare Vectorize** + Workers AI `bge-m3` | Similar questions, diagram match, small AI context |
| Backup | D1 Time Travel + daily R2 export + weekly Google Drive | See §9 |
| .docx export | `python-docx` + raw XML for RTL | Word 2007-compatible output |
| English grammar | **LanguageTool** (self-hosted Java server) | Free, offline, en-GB |
| Rule engine | Python (from `GRAMMAR-RULES.md`) | Free, instant, all 4 languages |
| Diagram labels | Fabric.js canvas | Put A/B/C markers on stored images |
| Code-drawn figures | SVG → PNG (CairoSVG) | Tables, timelines, concept maps, graphs |
| Fonts | Times New Roman, Noto Sans Devanagari, Jameel Noori Nastaleeq | Embedded name in docx; installed on PCs |

---

## 2. Modules

1. **Input** — paste text, upload .docx/.pdf, or photo (OCR).
2. **Parser** — splits into questions, detects type/language/marks.
3. **Checker** — rules → LanguageTool → AI (only if needed).
4. **Review screen** — teacher accepts/rejects suggestions side by side.
5. **Question bank** — filter by class, subject, chapter, type, marks, language; usage history.
6. **Diagram bank** — upload/crop images, tag them, add label markers, outline maps.
7. **Paper builder** — pick questions manually or auto-pick by marks blueprint.
8. **Layout engine** — applies template 3a/3b, paginates to A4 with fixed font sizes.
9. **Export** — question paper .docx + answer key .docx.
10. **Admin** — users, school branches, logo, dictionary, AI usage & cost report.

---

## 3. Full flow

```
[1] Input ──► [2] Clean ──► [3] Parse ──► [4] Validate ──► [5] Grammar ──► [6] Review
                                                                                  │
[12] History ◄── [11] Export ◄── [10] Layout ◄── [9] Build paper ◄── [8] Bank ◄── [7] Diagrams
```

| # | Step | Done by | API / engine | Cost |
|---|---|---|---|---|
| 1 | Input: typed / pasted / .docx | Code | — | Free |
| 1b | Input: photo of handwritten or printed paper | AI vision | **Gemini 3.8 Flash** (latest generation, strong on Indic + Urdu handwriting) | Under ₹1 per page |
| 2 | Clean: spaces, blanks, Unicode (Urdu ی ک ہ), NFC | Code | Rule engine | Free |
| 3a | Parse: numbering, Q-groups, marks, options | Code | Regex + `QUESTION-TYPES.md` keywords | Free |
| 3b | Parse fallback: messy text the rules can't split | AI | **Claude Haiku 5.5** → strict JSON schema | Paise |
| 4 | Validate: marks totals, 4 options, duplicates | Code | Python + Vectorize similarity | Free |
| 5a | Grammar: universal + language rules | Code | Rule engine | Free |
| 5b | Grammar English | Local server | **LanguageTool** (en-GB) | Free |
| 5c | Grammar Hindi / Marathi / Urdu wording | AI | **Claude Haiku 5.5** (only new questions, batched) | Paise |
| 5d | "Deep check" button (teacher asks) | AI | **Claude Sonnet 5.5** — on demand only | A few rupees |
| 6 | Review: accept / reject | Teacher | — | Free |
| 7a | Diagram match from bank | Code | Vectorize `diagrams` query | Free |
| 7b | Auto-tag a newly uploaded diagram | AI | **Gemini 3.8 Flash** (vision) | Paise |
| 7c | Tables, timelines, concept maps, graphs | Code | SVG generator | Free |
| 8 | Save to bank with history + embed | Worker | D1 + Workers AI bge-m3 → Vectorize | Free tier |
| 9a | Manual paper building | Teacher | — | Free |
| 9b | Auto-pick by blueprint (chapter + type + marks) | Code | Query + least-recently-used rule | Free |
| 10 | Layout & pagination (3a / 3b) | Code | Layout engine | Free |
| 11a | Export question paper .docx | Code | python-docx | Free |
| 11b | Answer key (when answers not stored) | AI | **Claude Haiku 5.5** — teacher verifies | Paise |
| 11c | Bilingual paper (English ⇄ Urdu, for UCC) | AI | **Claude Haiku 5.5**, Sonnet 5.5 for literary text | Paise |
| 12 | History: who made it, which questions, which exam | Worker | D1 | Free |

Rule of thumb: **code → cheapest AI → stronger AI only on teacher's click.**

---

## 4. Multi-model structure (AI gateway)

All AI calls go through one module: the AI gateway inside the Cloudflare Worker (`worker/`). Nothing else in the app calls an API directly.

```
ai_gateway.call(task="grammar_mr", payload=..., schema=...)
        │
        ├─ 1. cache lookup (hash of task + text)  → hit? return, ₹0
        ├─ 2. pick model from ROUTES table
        ├─ 3. send with cached system prompt (rules file)
        ├─ 4. validate JSON against schema → invalid? retry once, then fallback model
        ├─ 5. log tokens + cost to ai_log
        └─ 6. store in cache
```

### Routing table

| Task | Primary model | Fallback | Output |
|---|---|---|---|
| `ocr_page` | Gemini 3.8 Flash | Claude Haiku 5.5 (vision) | Plain text |
| `parse_fallback` | Claude Haiku 5.5 | Gemini 3.8 Flash | JSON (bank record) |
| `grammar_hi` / `grammar_mr` / `grammar_ur` | Claude Haiku 5.5 | Gemini 3.8 Flash | JSON issues list |
| `grammar_deep` | Claude Sonnet 5.5 | — | JSON issues list |
| `diagram_tag` | Gemini 3.8 Flash | Claude Haiku 5.5 | Tags JSON |
| `answer_key` | Claude Haiku 5.5 | Gemini 3.8 Flash | JSON answers |
| `translate` | Claude Haiku 5.5 | Claude Sonnet 5.5 | Text |

The routing table lives in `config/routes.json`, so you can swap models without changing code.

### Model policy — latest generation only

- Use only **current-generation** models (today: Claude Haiku 5.5, Claude Sonnet 5.5,
  Gemini 3.8 Flash). Never route to older generations just because the per-token price is lower.
  They need longer prompts, give wordier answers, break JSON more often and need retries, so the
  real cost per paper ends up higher.
- Judge models by **cost per finished task**, not price per token:
  `cost_per_task = (tokens_in + tokens_out + retry tokens) × rate`. `ai_log` records this per task.
- Haiku vs Sonnet within the same generation is a choice of *size*, not *age*. Haiku 5.5 handles the
  routine tasks. If `ai_log` shows Haiku retrying or missing errors on a task (for example Urdu
  grammar), move that task to Sonnet 5.5 in `routes.json`.
- **Upgrade rule:** when a new generation is released, test it on 10 saved sample papers.
  Switch only if cost per task and accuracy are equal or better.

### Efficiency rules

- **Batch:** send all new questions of one paper in one call, not one call per question.
- **Cache:** same text never goes to the API twice; bank questions are never re-checked.
- **Prompt caching:** the rules file is a fixed system prompt, which is billed cheaper when repeated.
- **Batch API (50% off):** use it for bulk jobs such as importing an old question bank overnight.
- **Text, not images:** OCR once, then work only on the text.
- **Strict JSON:** every AI reply follows a schema, so there's no re-asking and no parsing errors.
- **Monthly cap:** admin sets a ₹ limit. Once it's reached, AI features pause and code-only mode continues.
- **Keys:** stored encrypted on the server/admin PC, never inside the installer.

---

## 5. Database (Cloudflare D1)

| Table | Key fields |
|---|---|
| `questions` | id, class, subject, chapter, section, lang, type, sub_type, marks, text, options_json, answer_json, diagram_id, needs_source, difficulty, grammar_checked, created_by, created_on |
| `diagrams` | id, class, subject, chapter, tags, file_path, labels_json, kind (figure/map/code) |
| `papers` | id, school, class, subject, exam_name, month_year, marks, time, template (3a/3b), created_by, created_on, docx_path |
| `paper_items` | paper_id, question_id, q_group, order_no |
| `usage` | question_id, paper_id, exam_name, date |
| `dictionary` | lang, word |
| `users` | id, name, role (admin / teacher / checker), subjects |
| `ai_log` | time, task, model, tokens_in, tokens_out, cost_inr, cache_hit |
| `ai_cache` | hash, task, response_json |

---

## 6. Screens

1. **Dashboard** — recent papers, this month's AI spend, pending reviews.
2. **New paper** — header details form (class, subject, exam name, date, marks, time).
3. **Input workspace** — paste/upload on the left, parsed questions on the right.
4. **Review** — grammar suggestions inline (green = auto-fixed, yellow = suggestion, red = check).
5. **Bank** — filters, usage badges ("used in UT-I 2026"), add-to-paper button.
6. **Diagram bank** — upload, crop, tag, label-marker tool.
7. **Paper canvas** — live A4 preview, drag questions between groups, page fill % per sheet.
8. **Export** — question paper + answer key, file named
   `Class <N> <Subject> - Theory Paper.docx` / `- MCQ Paper.docx`.
9. **Admin** — users, logo, branches, dictionary, AI routes, monthly cap.

---

## 7. Folder structure

```
qp-software/
├─ app/                 # Tauri + React UI
├─ server/
│  ├─ main.py           # FastAPI
│  ├─ parser/           # rules from QUESTION-TYPES.md
│  ├─ checker/          # rules from GRAMMAR-RULES.md + LanguageTool client
│  ├─ ai_client.py      # calls the Worker's AI gateway (no keys here)
│  ├─ layout/           # template 3a / 3b pagination
│  ├─ export/           # python-docx builders
│  └─ figures/          # SVG generators
├─ worker/              # Cloudflare Worker: auth, D1, R2, Vectorize, ai_gateway (keys as secrets)
├─ config/│  ├─ routes.json       # model routing
│  └─ school.json       # name, address, logo, branches
├─ data/
│  ├─ offline-queue.sqlite   # cache only
│  ├─ diagrams/
│  └─ dictionary/en.txt hi.txt mr.txt ur.txt
└─ specs/               # all spec .md files
```

---

## 8. Build phases

| Phase | Deliverable | AI needed? |
|---|---|---|
| 1 | Header form + paste → parse → layout → .docx export (template 3a/3b) | No |
| 2 | Question bank + usage history + auto-pick | No |
| 3 | Rule engine + LanguageTool + review screen | No |
| 4 | Diagram bank + label tool + code-drawn tables/timelines/concept maps | No |
| 5 | AI gateway: parse fallback, Hindi/Marathi/Urdu grammar, answer key | Yes |
| 6 | OCR from photos, bilingual papers, diagram auto-tag | Yes |
| 7 | Multi-branch access, roles, cost dashboard (same Cloudflare backend) | Optional |

The software is usable for daily papers after **Phase 1**, and every later phase adds to it
without changing earlier work.

---

## 9. Storage service

Full spec: **`STORAGE-AND-RAG.md`**. Summary:

- **Cloudflare D1** = source of truth for all data (bank, papers, history, users, ai_log).
- **Cloudflare R2** = diagrams, logo, exported .docx.
- **Cloudflare Workers** = the only server: login, roles, AI gateway, API keys as secrets.
- **Vectorize + Workers AI bge-m3** = RAG for similar questions, diagram matching and small AI context.
- **Backups:** D1 Time Travel + daily export to R2 (30 days) + weekly export to Google Drive.
- The school PC keeps only an offline queue/cache. No Supabase.
- Cost: ₹0 to start; Workers Paid $5/month when the bank passes ~4,500 questions.

---

## 10. Testing checklist

- [ ] Class 9 Social Science sample produces exactly the reference 2+2 sheets
- [ ] Marks totals mismatch is blocked before export
- [ ] Urdu paper opens in Word 2007 with correct RTL and Nastaleeq font
- [ ] Hindi/Marathi conjuncts render correctly (no broken ZWJ)
- [ ] Same question pasted twice → cache hit, ₹0
- [ ] AI disabled → whole flow still works manually
- [ ] Monthly cap reached → AI buttons disabled with a clear message
