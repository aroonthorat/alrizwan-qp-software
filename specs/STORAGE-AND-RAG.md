# Storage & RAG — Cloudflare + Google Drive

Replaces local-first SQLite as the source of truth. The school PC is **not trusted** with data:
it only holds a temporary offline queue. No Supabase.

## 1. Services

| What | Service | Free limit (Oct 2026) | Notes |
|---|---|---|---|
| Question bank, papers, usage history, users, ai_log | **Cloudflare D1** (SQLite) | 5 GB, 5M rows read/day, 100k rows written/day | Same SQL as the plan's SQLite schema. Never pauses. |
| Diagrams, logo, exported .docx, OCR source images | **Cloudflare R2** | 10 GB, no egress fees | Private bucket; files served through the Worker only |
| API server: login, AI gateway, API keys | **Cloudflare Workers** | 100k requests/day | All AI keys live here as Worker secrets |
| RAG vectors | **Cloudflare Vectorize** | 5M stored dimensions (≈ 4,800 vectors at 1024 dims), 30M queried dims/month | See §4 |
| Embeddings | **Workers AI** `@cf/baai/bge-m3` | 10,000 neurons/day (≈ 9M tokens/day) | Multilingual: en, hi, mr, ur |
| Weekly off-site backup | **Google Drive** (school account) | 15 GB | Copy outside Cloudflare |

Upgrade path: **Workers Paid $5/month (≈ ₹440)** when the bank passes ~4,500 questions
(Vectorize limit) or limits are hit. Paid includes 10M stored dims, D1 25B reads / 50M writes per month.
Since 1 Sep 2026 free-plan D1 queries fail after the daily limit until midnight UTC — set Cloudflare
email alerts.

## 2. Architecture

```
School PC (Tauri app)
   │  HTTPS + login token
   ▼
Cloudflare Worker  ──►  D1 (data)        ──►  Time Travel restore (point-in-time)
   │                ──►  R2 (files)
   │                ──►  Vectorize (RAG) ◄── Workers AI bge-m3 (embeddings)
   │                ──►  AI models (Claude / Gemini / Nano Banana) via ai_gateway
   ▼
Cron Trigger (weekly) ──► export D1 + R2 index ──► Google Drive
```

- The desktop app never talks to D1, R2 or AI providers directly — only to the Worker.
- **Offline mode:** the app keeps a local queue (SQLite) of unsent edits and the last-opened papers.
  Queue syncs when online. Local data is a cache; deleting it loses nothing that was synced.
- Python FastAPI stays on the PC only for local work (docx export, layout, rule engine). It holds no keys.

## 3. Security & access

- Each teacher has a login; roles `admin / teacher / checker` enforced in the Worker.
- Teachers cannot delete bank questions — they archive; only admin hard-deletes.
- R2 bucket private; downloads via short-lived signed URLs from the Worker.
- API keys only as Worker secrets (`wrangler secret put`). Never in the app, repo or PC.

## 4. RAG system (so AI reads only what it needs)

Goal: every AI call gets a small, relevant context instead of whole papers → fewer tokens, better answers.

### What gets embedded (one vector each)

| Collection (Vectorize namespace) | Item | Text embedded |
|---|---|---|
| `questions` | each bank question | `type + chapter + text + options` |
| `diagrams` | each diagram | tags + extracted labels + caption |
| `rules` | each rule row in GRAMMAR-RULES.md / QUESTION-TYPES.md | rule ID + text |
| `syllabus` (optional, later) | textbook chapter chunks (~300 words) uploaded by admin | chunk text |

Vector metadata (for filtering before similarity): `class, subject, chapter, lang, type, item_id`.
The full record stays in D1/R2; Vectorize stores only the vector + metadata + ID.

### Uses

| Use | How | AI cost |
|---|---|---|
| Duplicate / near-duplicate warning when saving a question | query `questions`, same class+subject, score ≥ 0.92 | ₹0 |
| "Similar questions" in the bank and auto-pick variety | query `questions` | ₹0 |
| Match a figure question to a stored diagram | query `diagrams` with question text | ₹0 |
| Grammar check for hi/mr/ur | send only the top 8 matching `rules` with the questions | Smaller prompt |
| Answer key | send question + top 3 `syllabus` chunks of that chapter | Smaller prompt, grounded |
| Parse fallback | send top 5 `rules` for detected types | Smaller prompt |

### Rules

- Embed on save/approve only; re-embed only when text changes (hash check).
- Always filter by `class + subject` (and `lang`) before similarity search.
- Max context per AI call: top-k ≤ 8 items, ≤ 1,500 tokens.
- Answer keys and grammar suggestions must cite the item IDs they used (stored in `ai_log`).
- Never use RAG output to write a passage, poem or story (template rule still applies).

## 5. Backups

| Backup | Frequency | Keep |
|---|---|---|
| D1 Time Travel (built in) | continuous | restore to any minute in the retention window |
| D1 SQL export + R2 file list → R2 `backups/` | daily (Cron Trigger) | 30 days |
| Same export → Google Drive | weekly | 1 per month forever + 1 per exam season |
| Vectorize | not backed up — rebuilt from D1 by a re-index job | — |

Restore test once per term: restore the latest Drive backup into a test D1 database.

## 6. Monthly cost

| Stage | Cost |
|---|---|
| Start (≤ ~4,500 questions) | ₹0 |
| Growing bank / heavy use | $5 (≈ ₹440) Workers Paid + a few ₹ for R2 above 10 GB |

Check current limits on Cloudflare's pricing pages before launch.
