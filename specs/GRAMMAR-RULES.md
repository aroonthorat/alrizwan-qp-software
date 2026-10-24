# Al-Rizwan Question Paper Software — Grammar & Spelling Rules

Languages: **English · Hindi · Marathi · Urdu**

This file is the rule source for the software's checker. The order is:
1. Mechanical rule engine (this file) — free, offline, instant.
2. LanguageTool for English (free, self-hosted).
3. AI API only for Hindi / Marathi / Urdu wording issues the rules can't catch,
   and only on **new** questions (bank questions are already checked).

---

## 0. Golden rules (all languages)

- **Never auto-change wording.** Every wording fix is a *suggestion* the teacher accepts or rejects.
- Only `AUTO` fixes (spacing, Unicode, punctuation marks) may be applied silently — and even these
  are listed in a "changes made" log.
- Keep the teacher's meaning, numbering, "(any 5)", section names and marks exactly as written.
- Proper nouns, names, dates, formulas, chemical symbols, code and quoted text are **skipped**.
- Never rewrite or invent a passage (उतारा / اقتباس). If a passage is missing, flag it — don't fill it.

### Issue levels

| Level | Meaning | Action |
|---|---|---|
| `AUTO` | Mechanical, meaning-safe | Fix silently, log it |
| `FIX` | Clear error (spelling, agreement) | Show suggestion, one-click accept |
| `STYLE` | Consistency / house style | Show as soft hint |
| `CHECK` | Possible problem, needs teacher eye | Highlight only |

### Checker output format

```json
{
  "question_id": "Q2.3",
  "lang": "mr",
  "level": "FIX",
  "rule": "MR-SP-04",
  "original": "आणी",
  "suggestion": "आणि",
  "note": "Spelling of conjunction"
}
```

---

## 1. Universal rules (every language)

| ID | Level | Rule |
|---|---|---|
| U-01 | AUTO | Collapse double/multiple spaces into one; trim line start/end |
| U-02 | AUTO | No space **before** `, . ? ! : ; ।  ؟ ، ۔` ; one space **after** |
| U-03 | AUTO | Blanks: any run of `_`, `…`, `----`, `.....` → standard blank `____________` (12 underscores) |
| U-04 | AUTO | Brackets: `( 5 )` → `(5)`; marks pattern `10x1=10` → `10 × 1 = 10` |
| U-05 | AUTO | Unicode normalise to NFC; remove zero-width chars except ZWJ/ZWNJ needed by the script |
| U-06 | STYLE | Numbering continuous inside a group (1, 2, 3…) — flag gaps or repeats |
| U-07 | FIX | Marks totals: `count × marks` must equal the stated total; group totals must equal header marks |
| U-08 | STYLE | MCQ options parallel in form (all nouns / all years / all phrases); same case style |
| U-09 | CHECK | MCQ: exactly 4 options, no duplicates, no "All/None of these" mixed with a correct single option unless intended |
| U-10 | CHECK | Duplicate question inside the same paper (≥ 90% text match) |
| U-11 | STYLE | Digits consistent across one paper (all Western `0-9`, or all native) |
| U-12 | CHECK | Unclosed bracket or quote |

---

## 2. English (`en`)

Spelling standard: **Indian/British English** — colour, centre, organisation, labour, programme, metre.
Run LanguageTool with `en-GB`; the rules below are house rules on top.

| ID | Level | Rule |
|---|---|---|
| EN-01 | AUTO | Capitalise the first letter of every question and option |
| EN-02 | AUTO | Standalone `i` → `I` |
| EN-03 | FIX | Wh-questions (What, Why, How, Which, Who, When, Where) end with `?` |
| EN-04 | STYLE | Instructions (Explain, State, Name, Describe, Write) end with `.` |
| EN-05 | FIX | `a` / `an` by sound: an hour, an MLA, a university, a one-rupee coin |
| EN-06 | FIX | Common confusions: its/it's, their/there/they're, then/than, affect/effect, lose/loose, weather/whether, principal/principle |
| EN-07 | FIX | Subject–verb agreement: "The list of rivers **is**", "Each of the states **has**" |
| EN-08 | STYLE | US → UK spelling: color→colour, center→centre, organization→organisation |
| EN-09 | STYLE | Abbreviations consistent within a paper: `GDP` or `G.D.P.` — not both |
| EN-10 | STYLE | Headings use standard school phrasing (see §6) |
| EN-11 | FIX | Fill-in-the-blank: sentence must stay grammatical with the answer in place |
| EN-12 | CHECK | True/False statements must be a full statement, not a question |

---

## 3. Hindi (`hi`)

Standard: **केंद्रीय हिंदी निदेशालय** standard Devanagari spelling.

| ID | Level | Rule |
|---|---|---|
| HI-01 | AUTO | Sentence end uses पूर्ण विराम `।` — not `.` or `|` (pipe) |
| HI-02 | AUTO | Question sentences end with `?` |
| HI-03 | FIX | Standard forms: गई (not गयी), लिए (not लिये), हुए (not हुये), चाहिए (not चाहिये) |
| HI-04 | FIX | की / कि: `कि` is the conjunction ("कहा कि"), `की` is possessive/verb |
| HI-05 | FIX | है / हैं — number agreement with subject; `हैं` for plural & आप |
| HI-06 | FIX | Chandrabindu vs anusvara: हँसना, आँख, माँ (ँ for nasal vowel); संसार, हिंदी (ं) |
| HI-07 | STYLE | Panchamakshar → anusvara (modern standard): हिन्दी→हिंदी, सम्बन्ध→संबंध |
| HI-08 | FIX | Common matra errors: कृपया (not क्रपया), उज्ज्वल, आशीर्वाद, सामग्री, अत्यधिक |
| HI-09 | CHECK | Gender agreement of verb/adjective with noun (नदी बहती है / पर्वत ऊँचा है) |
| HI-10 | STYLE | Nukta only in Urdu-origin words where the school follows it (ज़मीन, फ़सल) — keep one style per paper |
| HI-11 | AUTO | Remove stray ZWJ/ZWNJ that break conjuncts |

Standard Hindi instruction headings: `रिक्त स्थानों की पूर्ति कीजिए।` · `सही विकल्प चुनकर लिखिए।` ·
`सही जोड़ियाँ मिलाइए।` · `सही या गलत लिखिए।` · `एक वाक्य में उत्तर लिखिए।` ·
`संक्षेप में उत्तर लिखिए।` · `विस्तार से उत्तर लिखिए।`

---

## 4. Marathi (`mr`)

Standard: **महाराष्ट्र शासन मान्य लेखनविषयक नियम** (Maharashtra government spelling rules).

| ID | Level | Rule |
|---|---|---|
| MR-01 | AUTO | Sentence end uses full stop `.` (modern Marathi) — convert `।` to `.` |
| MR-02 | AUTO | Eyelash ra `ऱ्य` / `ऱ्ह` where standard: वाऱ्याने, ऱ्हास, कोऱ्या (not वार्याने) |
| MR-03 | FIX | आणि (not आणी) · पाहिजे (not पाहीजे) · काही (not काहि) · नाही (not नाहि) |
| MR-04 | FIX | Final long vowel in Marathi words: मी, ती, ही, तू, ऊ-ending words per शासन नियम |
| MR-05 | FIX | Tatsam words keep original short/long i/u: परीक्षा, विद्यार्थी, गुरु, कवि→कवी (Marathi uses कवी) |
| MR-06 | STYLE | Anusvara on silent-nasal words per rules: `हे`/`हें` → modern `हे` (no old-style anusvara) |
| MR-07 | CHECK | Hindi words slipped in: `और` → `आणि`, `है` → `आहे`, `कि` (Hindi) → `की` |
| MR-08 | FIX | Number/gender agreement: मुले खेळतात, मुलगी आली, झाडे आहेत |
| MR-09 | AUTO | Question sentences end with `?` |

Standard Marathi instruction headings: `गाळलेल्या जागा भरा.` · `योग्य पर्याय निवडून विधाने पूर्ण करा.` ·
`जोड्या जुळवा.` · `चूक की बरोबर ते लिहा.` · `एका वाक्यात उत्तरे लिहा.` ·
`थोडक्यात उत्तरे लिहा.` · `सविस्तर उत्तरे लिहा.` · `कारणे लिहा.` · `संकल्पना चित्र पूर्ण करा.`

---

## 5. Urdu (`ur`)

Right-to-left. Font: **Jameel Noori Nastaleeq** (fallback: Noto Nastaliq Urdu). Must open in Word 2007.

### 5.1 Unicode — the most common source of errors (all `AUTO`)

Text pasted from InPage/Arabic keyboards often uses Arabic letters that look right but break search,
sorting and fonts:

| Wrong (Arabic) | Correct (Urdu) | Code |
|---|---|---|
| ي U+064A / ى U+0649 | ی | U+06CC |
| ك U+0643 | ک | U+06A9 |
| ه U+0647 (as final he) | ہ | U+06C1 |
| ه U+0647 (in aspirates: بھ، پھ) | ھ | U+06BE |
| ? | ؟ | U+061F |
| , | ، | U+060C |
| . (sentence end) | ۔ | U+06D4 |
| ; | ؛ | U+061B |

### 5.2 Spelling & grammar

| ID | Level | Rule |
|---|---|---|
| UR-01 | AUTO | Apply the Unicode table above |
| UR-02 | FIX | Standard forms: کیجیے (not کیجئے), لیے (not لئے), گئے, دیجیے |
| UR-03 | FIX | ے (bari ye) at word end where required: لڑکے، کے، سے (not لڑکی for plural) |
| UR-04 | FIX | Verb gender/number agreement: لڑکی آئی، لڑکے آئے |
| UR-05 | STYLE | Digits: one style per paper — Urdu `۰۱۲۳۴۵۶۷۸۹` (U+06F0–06F9) or Western |
| UR-06 | AUTO | English terms / numbers inside RTL lines wrapped with LRM/RLM so they don't flip |
| UR-07 | CHECK | Question numbering `(1)` and marks brackets render correctly in RTL |
| UR-08 | STYLE | Izafat and hamza kept as typed by the teacher — flag only, never auto-change |

Standard Urdu instruction headings: `خالی جگہ پُر کیجیے۔` · `صحیح متبادل منتخب کیجیے۔` ·
`جوڑ ملائیے۔` · `صحیح یا غلط لکھیے۔` · `ایک جملے میں جواب لکھیے۔` ·
`مختصر جواب لکھیے۔` · `تفصیل سے جواب لکھیے۔`

---

## 6. Standard English instruction headings (house style)

`Answer the following.` · `Fill in the blanks.` · `Choose the correct alternative.` ·
`Match the following.` · `State True or False.` · `Answer in one sentence.` ·
`Answer in brief.` · `Answer in detail.` · `Give reasons.` · `Distinguish between.` ·
`Write short notes.` · `Study the given figure and answer.` · `Map work.`

If a teacher's heading is close to one of these (e.g. "Answer in brief" vs "Answer briefly"),
raise a `STYLE` hint only — never replace it.

---

## 7. Dictionary & whitelist

Keep a per-school whitelist the checker never flags:
- School/branch names, teacher names, place names (Nanded, Chaitaniya Nagar)
- Subject terms from textbooks (Balbharati spellings win over dictionary spellings)
- Accepted words added by teachers (one-click "Add to dictionary")

Store as `dictionary/<lang>.txt`, one word per line.
