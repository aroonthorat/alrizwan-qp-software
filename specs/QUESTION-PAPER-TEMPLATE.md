# Al-Rizwan English School — Question Paper Generation Spec

Use this file as the authoritative build instruction. Given question content in ANY input form
(handwritten photos, typed text, PDF, or a bare list), produce a question paper matching one of
two locked templates:

- **Template 3a — THEORY paper** (descriptive questions, figures, map work)
- **Template 3b — MCQ paper** (objective questions, 2-column booklet; NEET-style option layout)

Never invent a new layout. Never drop the header block, page borders, or watermark.
Do not add signature lines (removed by design).

---

## 0. Inputs the user provides

| Input | Use |
|---|---|
| Logo image file | header mark + centre watermark (same file, used twice) |
| Handwritten image / typed text of questions | the question content only |
| Header details (class, subject, date, marks, unit test, time) | header table |
| **Paper name / exam title** (e.g. "First Unit Test", "Half Yearly Exam", "NEET Practice Test") | the third header line, uppercased |

If any header detail is missing, ask once; do not guess marks or timings.
The **paper name always comes from the user** — never assume "NEET". Print it verbatim in caps
with the month/year appended when given, e.g. `FIRST UNIT TEST — AUG. 2026`,
`HALF YEARLY EXAMINATION — OCT. 2026`, `MCQ TEST — AUG. 2026`.
If input is handwritten, transcribe verbatim — keep the teacher's wording, numbering,
"(any 5)", marks in brackets, and section names exactly as written. Fix only obvious spelling.

---

## 1. Shared shell (both templates)

- Page width **794px** (A4 at 96dpi). Serif throughout: `'Times New Roman', Georgia, serif`. Ink `#111`.
- **Page border:** a single `border:4px double #1a1a1a`, inset 8mm from the paper edge. No second
  frame line.
- **Watermark:** the logo, absolutely positioned, `top:50%; left:50%;
  transform:translate(-50%,-50%); width:480px; opacity:.07; filter:grayscale(1); z-index:0;
  pointer-events:none`, with the content body at `z-index:1` so the watermark sits BEHIND the
  text. Use one fixed appearance — no `@media print` override — so screen and print match exactly
  (printers lay ink at full strength; a screen-tuned colour watermark comes out far darker).
- **Header row:** flex — logo `width:96px` (3a) / `90px` (3b) · centre block · Roll No. box group.
  Bottom rule `border-bottom:2.5px solid #1a1a1a`.
  - School name `font-size:34px` (3a) / `32px` (3b), bold.
  - Address line `Chaitaniya Nagar Road, Nanded` at 14px / 13px.
  - Third line, bold + letterspaced caps: **the paper name the user gave**, e.g.
    `FIRST UNIT TEST — AUG. 2026`, `MCQ TEST — AUG. 2026`, `NEET PRACTICE TEST — SEP. 2026`.
  - Roll No. = 4 empty boxes, each `width:22px; height:26px; border:1px solid #1a1a1a`, gap 3px.
- **Header details table:** full-width, `border-collapse:collapse`, every cell
  `border:1px solid #1a1a1a; padding:6px 10px`. Labels plain, values bold.
  Row 1: Class · Subject · Date. Row 2: Marks · Unit Test · Time.
  Last row spans the table: `Name of the Student :` + dotted-underline fill.
  Omit any row/cell the user didn't supply — never print an empty label.
  School name is always `Al-Rizwan English School` unless the user names a different branch
  from the group (the logo covers the whole group of schools).
- **No signature block.** Paper ends with the last question (3a) or the rough-work box (3b).

---

## 2. Template 3a — THEORY

Type scale (A4, locked): question text **16px / line-height 1.8**; question headings
**17.5px bold**; header table 15px; school name 32px. Never go below 16px for question text —
the same scale is used from KG to 12th, so text size is never traded for fitting a page.

Question block pattern — one heading line per question group, marks in brackets at the end:

```
Q.1) Answer the following.            (10 × 1 = 10)
Q.2) Answer in brief. (any 5)         (5 × 2 = 10)
Q.3) Study the given figure and answer.  (3 + 3 = 6)
Q.4) Answer in short. (any 3)         (3 × 3 = 9)
Q.5) Map work.                        (5)
```

Sub-questions are numbered `1.` `2.` `3.` … restarting inside each Q group, one per line.

### Diagram handling (important)
Any question needing a figure, graph, table, or map gets a **placeholder box** beside the text,
never a drawn illustration:

- Box style: `border:1px solid #1a1a1a`, hatched fill
  `repeating-linear-gradient(45deg,#f4f2ec,#f4f2ec 6px,#fff 6px,#fff 12px)`,
  centred monospace caption at 11px `#666`.
- Figure box ≈ `280×175px`, laid out left of the question text in a flex row, `gap:14px`.
- Map box ≈ `560×620px` (a real drawing area — students mark on it), centred BELOW its instruction
  text (never beside it: a side-by-side map squeezes the labels into ragged two-line wraps).
- **Grow these to absorb leftover space** on a sheet that would otherwise end short; never shrink
  them below the sizes above.
- Caption names what goes there, e.g. `FIGURE 1 / layers of the atmosphere / (paste diagram here)`
  or `OUTLINE MAP OF INDIA / (attach / paste)`.
- If the source image contains a real diagram, still use the placeholder box and name it — the
  teacher pastes the original. Do not redraw it.

---

## 3. Template 3b — MCQ paper

Use 3b whenever **most or all** provided questions carry options — it is the general MCQ format,
not a NEET-only one. NEET is just the option/column styling; the paper is titled by whatever name
the user gives. Question count is whatever the user supplies (20, 25, 40, 50 …) — adjust the
instruction line and marks total to match; do not force 40.

- Header as above, then header details table with 4 columns:
  Class · Subject · Unit Test · Date / Questions · Max. Marks · Time (spans 2) /
  Name of the Student (spans 3) · Roll No.
- **Instructions box** — `border:1px solid #1a1a1a; padding:8px 12px; font-size:12.5px`,
  heading `IMPORTANT INSTRUCTIONS` bold + letterspaced, then three numbered lines:
  1. paper contains **N questions** (in M sections, if sectioned), all compulsory;
  2. each question carries **1 mark**, only ONE of (1)–(4) is correct;
  3. darken the OMR circle with blue/black ball pen; rough work in the space provided.
- **Body:** `display:grid; grid-template-columns:1fr 1fr; gap:0 20px; font-size:14px;
  line-height:1.5`. Left column carries `border-right:1px solid #bbb; padding-right:14px`.
  MCQ text never below 14px.
- **Section headers:** centred, bold, 13px, letterspaced caps, ruled above and below
  (`border-top`/`border-bottom:1px solid #1a1a1a; padding:3px 0`), e.g.
  `SECTION A — HISTORY`, `SECTION B — GEOGRAPHY`, `SECTION C — CIVICS`, `SECTION D — ECONOMICS`.
  Sections come from the subject; for single-topic papers use `SECTION A`, `SECTION B`… by chapter.
  If the teacher supplied no sections and the questions are one continuous set, **omit section
  headers entirely** and run the questions straight through both columns.
- **Question format** — NEET style, stem then a 2×2 option grid, options numbered `(1)`–`(4)`:

  ```
  12. The Deccan Plateau lies mainly in
      (1) North India      (2) South India
      (3) East India       (4) West India
  ```
  Markup: stem text, then `<div style="display:grid;grid-template-columns:1fr 1fr;gap:0 12px">`
  holding the four options. Each question wrapper `margin-bottom:3px`.
  **The `gap:0 12px` is required** — without a column gap a long option (e.g. "Gross Domestic
  Product") fills its track exactly and the next option's "(2)" butts straight onto it.
- Questions run **continuously 1…N** across sections (never restart numbering per section).
- Questions flow down the left column, then continue in the right column — balance so both
  columns end near the same height.
- **Rough work box** at the end: `border:1px solid #1a1a1a; height:70px; padding:5px 10px`,
  italic 12px label `Space for rough work`.
- If an MCQ needs a figure, insert the same hatched placeholder box (≈200×120px) under the stem.

---

### Pagination — text size wins over page count

Never squeeze a paper onto fewer sheets. Use as many A4 sheets as the locked type scale needs,
and instead balance the sheets so none looks empty:

- **A4 only.** The sheets are authored to fill A4's 1032px content box; Letter is 67px shorter and
  silently clips questions, so no paper-size control is exposed.
- Page margins (equal on all four sides, top and bottom alike): the 12mm outer margin is
  `padding` on `.page` itself, so it cannot vary between a full sheet and an empty one.
  A **single** `4px double` border, no inner frame line. Exact markup in §7.
  Measured result: 12mm (45px) on all four sides of every sheet.
- Aim for **85–95% vertical fill** on every sheet except the last, and never below ~60% on the
  last one — if the remainder is thin, pull a question group back from the previous sheet, or give
  map/figure work the extra room (a bigger drawing box is real space, not filler).
- Break at question-group boundaries (`Q.3`, `Q.4`…) for theory and at section boundaries for MCQ;
  never split a question or its options across sheets.
- Continuation sheets carry **no header strip** — they open directly on the next question group
  (`Q.4) Answer in short.`) or section (`SECTION C — CIVICS`). Identification lives in the footer
  line instead (see below), so no vertical space is spent repeating the masthead.
- **Footer line** (in the outer margin, `bottom:3.5mm`, centred, 10px `#555`, outside the border,
  on EVERY sheet): `Al-Rizwan English School · Class 9th · Social Science · <Paper name> · Page n of N`.
  This is what identifies a loose sheet — never reduce it to a bare page numeral.
- The previous sheet closes with an italic note, e.g. `Q.4 and Q.5 continue on page 2 →`.
- Rough-work box goes on the **last** MCQ sheet only, and its height absorbs that sheet's
  remainder (60px minimum, ~100px when there is room).
- Verified reference fill: theory 95% / 95%, MCQ 99% / 95%.
- Measured reference (Class 9 Social Science, 40 marks): theory = 2 sheets (Q1–Q3 / Q4–Q5 with the
  large map), 40-question MCQ = 2 sheets (Sections A+B / C+D).
- Always measure before delivering: inner-frame inset equal on all four sides, `scrollHeight ==
  clientHeight` per sheet, and fill within the range above.

---

## 4. Conversion rules when reading teacher input

1. Detect paper type: if **the majority of questions carry options** (A/B/C/D or 1/2/3/4) → **3b**
   (pure MCQ paper). If none or only a few do → **3a**, with the odd objective question placed
   inside a `Q.1) Choose the correct alternative.` group.
2. Group questions by the marks pattern the teacher used; build Q.1/Q.2/… headings and compute
   `(count × marks = total)` — the totals must add up to the Marks value in the header.
3. Convert every option set to NEET numbering `(1) (2) (3) (4)`, even if the source used A/B/C/D.
4. Preserve section names from the source; if none, derive them by topic.
5. Any mention of "figure", "diagram", "map", "graph", "given table" → add a placeholder box.
6. Add sheets rather than shrinking type: keep the locked scale and paginate per section 3.5.

---

## 5. Checklist before delivering

- [ ] Logo in header **and** as centre grayscale watermark at 7% opacity, behind the text
- [ ] Single `4px double` border, 12mm from the paper edge on all four sides
- [ ] School name, address, exam title, Roll No. boxes present
- [ ] Header details table complete, values bold
- [ ] Marks in every question heading; totals match header marks
- [ ] Theory text 16px / MCQ text 14px — never smaller, at any class level
- [ ] Every sheet 85–95% full (last sheet ≥ ~60%), nothing clipped at the bottom edge
- [ ] Diagram/map placeholders for all figure-based questions
- [ ] Paper name printed exactly as the user gave it (not assumed)
- [ ] MCQ: instructions box, sections only if supplied, continuous 1–N numbering, rough-work box
- [ ] Footer line with school, class, subject, paper name and `Page n of N` on every sheet

---

## 6. Copy-ready skeletons

**Page + watermark + header (both templates — swap sizes per template):**

```html
<section class="page" style="padding:12mm;height:297mm;background:#fff;font-family:'Times New Roman',Georgia,serif;color:#111;box-sizing:border-box;position:relative;overflow:hidden;display:flex;align-items:stretch">
  <div style="position:absolute;bottom:3.5mm;left:12mm;right:12mm;text-align:center;font-size:10px;color:#555;z-index:3">Al-Rizwan English School &#183; Class 9th &#183; Social Science &#183; PAPER NAME &#183; Page 1 of 2</div>
  <div style="position:relative;box-sizing:border-box;flex:1;min-width:0;height:273mm;border:4px double #1a1a1a;overflow:hidden">
  <img src="LOGO" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:480px;opacity:.07;filter:grayscale(1);z-index:0;pointer-events:none">
  <div style="position:absolute;inset:0;box-sizing:border-box;padding:22px;z-index:1;overflow:hidden">
    <div style="display:flex;gap:14px;align-items:center;border-bottom:2.5px solid #1a1a1a;padding-bottom:12px;margin-bottom:12px">
      <img src="LOGO" style="width:96px;height:auto">
      <div style="flex:1;text-align:center">
        <div style="font-size:34px;font-weight:700;line-height:1.12">Al-Rizwan English School</div>
        <div style="font-size:14px">Chaitaniya Nagar Road, Nanded</div>
        <div style="font-size:13.5px;font-weight:700;letter-spacing:1px;margin-top:3px">PAPER NAME — MONTH YEAR</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:12px;margin-bottom:3px">Roll No.</div>
        <div style="display:flex;gap:3px">
          <span style="width:22px;height:26px;border:1px solid #1a1a1a"></span>
          <span style="width:22px;height:26px;border:1px solid #1a1a1a"></span>
          <span style="width:22px;height:26px;border:1px solid #1a1a1a"></span>
          <span style="width:22px;height:26px;border:1px solid #1a1a1a"></span>
        </div>
      </div>
    </div>
    <!-- header details table, then questions -->
  </div>
  </div>
</section>
```

**3a question group + figure row:**

```html
<div style="font-weight:700;font-size:17.5px;margin:18px 0 8px">Q.3) Study the given figure and answer. &nbsp;(3 + 3 = 6)</div>
<div style="display:flex;gap:18px;align-items:flex-start">
  <div style="width:240px;height:150px;border:1px solid #1a1a1a;background:repeating-linear-gradient(45deg,#f4f2ec,#f4f2ec 6px,#fff 6px,#fff 12px);display:flex;align-items:center;justify-content:center;text-align:center;flex:none">
    <span style="font:11px ui-monospace,Menlo,monospace;color:#666">FIGURE 1<br>caption<br>(paste diagram here)</span>
  </div>
  <div style="font-size:16.5px;line-height:2">
    <div>1. …</div>
    <div>2. …</div>
  </div>
</div>
```

**3b column body + one question:**

```html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0 20px;font-size:14px;line-height:1.5">
  <div style="border-right:1px solid #bbb;padding-right:20px">
    <div style="text-align:center;font-weight:700;font-size:13px;letter-spacing:1px;border-top:1px solid #1a1a1a;border-bottom:1px solid #1a1a1a;padding:3px 0;margin-bottom:7px">SECTION A — HISTORY</div>
    <div style="margin-bottom:7px">1. The First World War began in the year
      <div style="display:grid;grid-template-columns:1fr 1fr">(1) 1912<span>(2) 1914</span>(3) 1918<span>(4) 1920</span></div>
    </div>
  </div>
  <div><!-- continuation --></div>
</div>
<div style="border:1px solid #1a1a1a;height:100px;margin-top:8px;padding:8px 12px;font-size:12.5px;font-style:italic">Space for rough work</div>
```

---

## 7. Output

Deliver as an HTML file that prints to A4 with no scaling. One paper per file; name it
`Class <N> <Subject> <Paper Name>.html`. If both a theory and an MCQ paper are requested from the
same input, produce two separate files.

### PDF-ready build (reference: `Question Paper PDF Templates.dc.html`)

- Wrap the papers in `<doc-page size="a4">` with one `<section class="page">` per printed sheet
  (`doc-page.js` in the project owns print geometry — never write your own `@page` rule).
- Sheet structure — these literal values are what keep the margins equal; do not parameterise them:
  1. `<section class="page">` — `padding:12mm; height:297mm; box-sizing:border-box;
     position:relative; overflow:hidden; display:flex; align-items:stretch`.
     The height must be a **literal absolute value**. Never `var(--doc-page-h)`: `<doc-page>`
     measures its own pages, so sizing from its variable creates a ResizeObserver loop that
     freezes the page (no console error, just a dead main thread). Never omit it either — the
     content body is absolutely positioned, so the sheet would collapse to padding height and
     clip every question.
  2. footer line, absolutely placed in that margin at `bottom:3.5mm`.
  3. bordered box — `flex:1; min-width:0; height:273mm` (297mm − 2×12mm padding);
     `border:4px double #1a1a1a; overflow:hidden`. In a ROW flex container `flex:1` sets width
     only, so the height must be stated.
  4. watermark image, then the content body `position:absolute; inset:0; padding:22px; z-index:1;
     overflow:hidden`.
- **Nothing may overflow a sheet.** Measure the inner body: `scrollHeight` must equal
  `clientHeight`. If it overflows, move a question group to the next sheet — never shrink type.
- **Theory:** ~2 sheets for a 40-mark paper at the locked scale.
- **MCQ, 40 questions:** two A4 sheets — Sections A+B (Q1–20) on sheet 1, Sections C+D (Q21–40) on
  sheet 2. Ten questions per column, two columns per sheet, rule between. Sheet 1 ends with the
  continuation note; sheet 2 ends with the rough-work box. Page 2 opens straight on its next
  section — the footer line identifies it.
- Fewer questions (20–25) fit a single A4 sheet — one page, footer reads `Page 1 of 1`.
- Export via the PDF/print dialog; pages come out at true A4 with no browser headers.

### Tweakable controls

`Question Paper PDF Templates.dc.html` exposes five props (Tweaks panel), read as
`this.props.x ?? default`:

| Prop | Control | Default | Effect |
|---|---|---|---|
| `showWatermark` | toggle | on | centre logo watermark on every sheet |
| `watermarkOpacity` | 0.03–0.20 | 0.07 | watermark strength, identical on screen and print |
| `showPageNumber` | toggle | on | page numeral in the bottom outer margin |
| `showInstructions` | toggle | on | IMPORTANT INSTRUCTIONS box on the MCQ sheet |
| `showRoughWork` | toggle | on | rough-work box on the last MCQ sheet |

Keep these as props — never hand-roll a controls panel. Text like the school name, class, subject
and paper title is edited directly in the document, not through tweaks.
- **Deliver BOTH formats every time:** a print-ready PDF (via the export dialog, A4) *and* an
  editable Word `.doc` per paper, so the teacher can correct a question without regenerating.
- **Editable Word copy:** emit a `.doc` (Word-compatible HTML) per paper — same markup, logo
  embedded as a base64 data URI, `@page{size:21cm 29.7cm;margin:1.2cm}`, and
  `<br style="page-break-before:always">` between sheets. Strip `sc-if` wrappers and any
  `position:absolute` (Word ignores it) when converting. Teachers open it in Word to edit text.
- File naming: `<Class> <Subject> - Theory Paper.doc` / `- MCQ Paper.doc`.
