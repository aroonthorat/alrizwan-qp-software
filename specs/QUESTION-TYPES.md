# Al-Rizwan Question Paper Software — Question Types

Every question in the bank has one `type` from this file. The type decides:
how the question is **detected** from pasted text, what **fields** it stores, how it is **rendered**
in the paper template, and whether it needs a **diagram**.

Languages: **English (en) · Hindi (hi) · Marathi (mr) · Urdu (ur)**.

---

## 0. Global rules

- Paper layout follows `QUESTION-PAPER-TEMPLATE.md` (Theory 3a / MCQ 3b).
- Template choice: if most questions are `MCQ` → **3b**; otherwise **3a**.
- Group heading format: `Q.n) <heading>  (count × marks = total)`; choice groups add `(any N)`.
- Group totals must equal the header marks.
- **Answer space:** Class 4th and above use a separate answer sheet, so no writing space for any
  type. KG–3rd: answer lines per type (setting `answer_lines`, default shown below).
- **Never generate a passage, poem or story** for a question. If the source text is missing, save
  the question with `needs_source: true` and leave the passage empty.
- Options are always printed `(1) (2) (3) (4)`, whatever the input used (A/B/C/D, a/b/c/d, क/ख, अ/ब).

---

## 1. Objective types

| Type ID | Name | Typical marks | Answer lines (KG–3) |
|---|---|---|---|
| `MCQ` | Choose the correct alternative | 1 | 0 |
| `FILL_BLANK` | Fill in the blanks | 1 | 0 |
| `TRUE_FALSE` | State True or False | 1 | 0 |
| `ONE_WORD` | Answer in one word | 1 | 1 |
| `ONE_SENTENCE` | Answer in one sentence | 1 | 1 |
| `MATCH` | Match the pairs | 1 per pair | 0 |
| `ODD_ONE` | Find the odd one out | 1 | 1 |
| `CORRECT_STMT` | Correct the wrong statement | 1 | 2 |
| `ARRANGE` | Arrange in order (chronological / size / sequence) | 1–2 | 1 |
| `COMPLETE_TABLE` | Complete the table | 2–3 | 0 |
| `TIMELINE` | Complete the timeline | 2–3 | 0 |
| `CONCEPT_MAP` | Complete the concept map / flowchart | 2–3 | 0 |

### Detection keywords

| Type | en | hi | mr | ur |
|---|---|---|---|---|
| MCQ | choose the correct, select | सही विकल्प | योग्य पर्याय | صحیح متبادل |
| FILL_BLANK | fill in the blanks | रिक्त स्थान | गाळलेल्या जागा, रिकाम्या जागा | خالی جگہ |
| TRUE_FALSE | true or false | सही या गलत | चूक की बरोबर | صحیح یا غلط |
| MATCH | match | जोड़ियाँ मिलाइए | जोड्या जुळवा | جوڑ ملائیے |
| ONE_SENTENCE | one sentence | एक वाक्य | एका वाक्यात | ایک جملے |
| ODD_ONE | odd one out | बेमेल | गटात न बसणारा | بے جوڑ |
| CONCEPT_MAP | concept map, flowchart | संकल्पना चित्र | संकल्पना चित्र, ओघतक्ता | تصوراتی خاکہ |

Line-level fallback: a line followed by 4 option lines → `MCQ`; a line containing `____` → `FILL_BLANK`;
a line ending `(True / False)` → `TRUE_FALSE`.

### Render rules

- **MCQ** — stem, then 2×2 option grid (`gap:0 12px`). In a 3a paper they sit in a
  `Choose the correct alternative.` group.
- **FILL_BLANK** — blank is exactly `____________`. Optional word bank in brackets after the
  sentence: `(Maharashtra, Gujarat, Karnataka)`.
- **TRUE_FALSE** — append ` (True / False)` (hi: `(सही / गलत)`, mr: `(चूक / बरोबर)`, ur: `(صحیح / غلط)`).
- **MATCH** — two-column bordered table, column headers `A` / `B` (hi `अ / ब`, mr `अ / ब`, ur `الف / ب`).
  Column B is **shuffled** at print time; the correct mapping is stored for the answer key.
  Column B may hold one extra distractor.
- **COMPLETE_TABLE / TIMELINE / CONCEPT_MAP** — **drawn by code** from stored data (see §5).
  Blank cells or boxes are printed empty. No image, no AI.

---

## 2. Descriptive types

| Type ID | Name | Typical marks | Answer lines (KG–3) |
|---|---|---|---|
| `SHORT` | Answer in brief | 2 | 3 |
| `SHORT3` | Answer in short | 3 | 4 |
| `LONG` | Answer in detail | 4–5 | 6 |
| `REASON` | Give reasons | 2–3 | 3 |
| `DIFFERENCE` | Distinguish between | 2–3 | 0 (table) |
| `SHORT_NOTE` | Write short notes | 3 | 4 |
| `EXPLAIN_TERM` | Explain the term / concept | 2 | 3 |
| `OPINION` | Express your opinion | 2–3 | 3 |

Render: numbered list under the group heading, 16px, one question per line.
`DIFFERENCE` may print a 2-column table with the two terms as headers (KG–3 only).

---

## 3. Figure, diagram & map types

| Type ID | Name | Diagram source |
|---|---|---|
| `FIGURE_QA` | Study the given figure and answer | Diagram bank image |
| `LABEL` | Label the parts marked A, B, C | Diagram bank image + label markers |
| `DRAW_LABEL` | Draw a neat labelled diagram | None — answer sheet |
| `MAP_MARK` | Mark and label on the outline map | Outline map bank |
| `GRAPH` | Draw / read a graph | Code-drawn axes and data |
| `GEO_CONSTRUCT` | Geometry construction / figure | Code-drawn |

Render: placeholder box from the template (figure ≈ 280×175px beside the text; map ≈ 560×620px
below the text). If the bank has a matching image, it replaces the hatched placeholder.

---

## 4. Language-paper types (English / Hindi / Marathi / Urdu subjects)

| Type ID | Name | Rule |
|---|---|---|
| `PASSAGE` | Comprehension passage + sub-questions | Passage text **only from the teacher**; never generated |
| `POEM` | Poem-based questions / appreciation | Poem text only from the teacher / textbook |
| `GRAMMAR_ITEM` | Do as directed (voice, narration, tense, transform) | Sub-type stored: `voice`, `narration`, `tense`, `synonym`, `antonym`, `punctuate`, `sandhi`, `samas`, `vachan`, `ling`, `kaal` |
| `LETTER` | Letter / application writing | No writing space Class 4+ |
| `ESSAY` | Essay writing | Topic list, "(any one)" |
| `STORY` | Story writing / complete the story | Outline points from teacher only |
| `DIALOGUE` | Dialogue writing | No writing space Class 4+ |
| `NOTICE_AD` | Notice / advertisement / news report | No writing space Class 4+ |
| `SUMMARY` | Summary / précis | Needs source passage |
| `TRANSLATE` | Translation | Stores source text + target language |

---

## 5. Maths & Science types

| Type ID | Name | Notes |
|---|---|---|
| `SOLVE` | Solve / simplify | Supports fractions, powers, roots (store as MathML / LaTeX) |
| `WORD_PROBLEM` | Word problem | |
| `PROVE` | Prove the theorem / result | |
| `NUMERICAL` | Science numerical | Units kept exactly as typed |
| `EQUATION` | Write / balance the chemical equation | Subscripts kept |
| `PRACTICAL` | Experiment / activity based | Optional figure |

---

## 6. Question bank record (one per question)

```json
{
  "id": "SS9-GEO-0142",
  "class": "9",
  "subject": "Social Science",
  "chapter": "Atmosphere",
  "section": "Geography",
  "lang": "en",
  "type": "MCQ",
  "sub_type": null,
  "marks": 1,
  "text": "The ozone layer is found in the",
  "options": ["Troposphere", "Stratosphere", "Mesosphere", "Thermosphere"],
  "answer": 2,
  "pairs": null,
  "table": null,
  "diagram_id": null,
  "needs_source": false,
  "difficulty": "easy",
  "grammar_checked": true,
  "created_by": "teacher_name",
  "created_on": "2026-08-01",
  "used_in": [
    { "paper_id": "9-SS-UT1-2026", "exam": "First Unit Test", "date": "2026-08-12" }
  ]
}
```

Type-specific fields:
- `MATCH` → `"pairs": [["Godavari","Maharashtra"], ...], "extra": ["Kerala"]`
- `COMPLETE_TABLE` → `"table": {"headers":[...], "rows":[[...]], "blanks":[[r,c], ...]}`
- `TIMELINE` → `"events": [{"year":1914,"label":"WWI begins","blank":false}, ...]`
- `CONCEPT_MAP` → `"nodes": [{"id":1,"text":"Atmosphere"}, {"id":2,"text":"","parent":1}]`
- `GRAMMAR_ITEM` → `"sub_type": "voice"`
- `PASSAGE` / `POEM` → `"source_text": "..."`, `"sub_questions": ["id", ...]`

---

## 7. Exam types (paper names)

Printed exactly as the teacher gives them, uppercased with month/year:

`UNIT TEST (I / II)` · `FIRST TERM / HALF YEARLY EXAMINATION` · `SECOND TERM / ANNUAL EXAMINATION` ·
`WEEKLY TEST` · `PRELIM EXAMINATION` · `MCQ TEST` · `NEET / JEE / CET PRACTICE TEST`

Stored on the paper record so history can answer:
"Which questions were used in Class 9 Social Science Unit Test I last year?"

---

## 8. Repetition rules (history)

- Warn when a question was used in the **same class & subject within the last 2 exams**.
- Auto-pick mode prefers questions with the oldest `used_in` date, balanced across chapters.
- Never repeat a question inside the same paper.
