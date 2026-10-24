# Al-Rizwan Question Paper Software

Desktop software built for **Al-Rizwan English School** (Nanded, Maharashtra) that turns pasted or uploaded questions into finished question papers in the school's locked templates (**Template 3a Theory** / **Template 3b MCQ**), checks grammar (English, Hindi, Marathi, Urdu), and maintains a local question bank with historical exam usage.

---

## Features (Phase 1)

1. **Header Details Form**: Class, Subject, Exam Title, Month-Year, Date, Marks, Time, and Roll No. box count.
2. **Deterministic Rule Parser (Offline / Zero AI)**:
   - Question groups (`Q.1)`, `Q.2)`...), sections (`SECTION A — HISTORY`...), marks breakdown `(10 × 1 = 10)`, `(any N)`.
   - Option detection and normalization into NEET standard `(1)`, `(2)`, `(3)`, `(4)`.
   - Automatic hatched figure (`280×175px`) and map (`560×620px`) placeholder insertion.
3. **Template Selector**: Majority MCQ $\rightarrow$ Template 3b; otherwise Template 3a (with manual toggle option).
4. **Validation Guardrails**:
   - Total calculated marks must match header Max Marks.
   - MCQs must contain exactly 4 options.
   - **Hard export block** on any mismatch with explanatory errors.
5. **Locked A4 Live Preview**:
   - Exact 794px width (A4 @ 96dpi), 12mm margins.
   - Single `4px double #1a1a1a` border inset.
   - 7% opacity grayscale watermark behind content.
   - Locked type scale: Theory 16px (headings 17.5px) / MCQ 14px.
   - Multi-sheet pagination with continuation notes.
6. **Word 2007 Compatible .docx Export**:
   - Exports clean Word documents matching the template.
   - Files named: `Class <N> <Subject> - Theory Paper.docx` / `- MCQ Paper.docx`.

---

## Windows Installation & Run Guide

### Prerequisites
- **Python 3.11+** installed and added to PATH.
- **Node.js 18+** and `npm` installed.

### Step 1: Install Python Dependencies
In PowerShell at the project root (`e:\Codespace\alrizwan-qp-software`):
```powershell
python -m pip install fastapi uvicorn[standard] python-docx pydantic pillow lxml pytest
```

### Step 2: Install Frontend Dependencies
```powershell
cd app
npm install
npm run build
cd ..
```

### Step 3: Run the Application
You can run the FastAPI backend (which also serves the compiled frontend) or run both dev servers:

#### Option A: Single Command (Production Server)
```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
Open your browser at: **`http://127.0.0.1:8000`**

#### Option B: Development Mode (Hot Reload)
- **Terminal 1 (Backend):**
  ```powershell
  python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Terminal 2 (Frontend with Vite):**
  ```powershell
  cd app
  npm run dev
  ```
  Open your browser at: **`http://localhost:5173`**

---

## Running Automated Tests

Run the test suite using `pytest`:
```powershell
python -m pytest tests/test_phase1.py -v
```

All tests verify:
- Parsing `samples/class9-social-science-theory.txt` $\rightarrow$ 2 Theory sheets (40 marks, Template 3a).
- Parsing `samples/class9-social-science-mcq.txt` $\rightarrow$ 2 MCQ sheets (40 questions, Template 3b).
- Marks mismatch blocks export with HTTP 400.
- Valid `.docx` generation with correct file names and valid OpenXML structures.

---

## Phase 1 Deliverables & Verification

- `samples/class9-social-science.txt` provides reference 40-mark Theory (Q1–Q5 with figure and map work) and 40-question MCQ (Sections A, B, C, D) papers.
- Generated documents are saved to `data/` and downloaded directly through the browser.
