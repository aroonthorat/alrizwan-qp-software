# Architectural & Implementation Decisions

## Decision Log

### 1. Phase 1 Parser Architecture
- **Decision:** Use deterministic regex and tokenizer rules according to `specs/QUESTION-TYPES.md` and `specs/GRAMMAR-RULES.md`.
- **Reason:** Complete offline functionality with zero AI dependency in Phase 1 as mandated by the specs.
- **Rules implemented:**
  - Question group detection: `Q.1)`, `Q.2)`, `Q. 1.`, etc.
  - Marks detection: `(10 × 1 = 10)`, `(5 × 2 = 10)`, `(3 + 3 = 6)`, `(any 5)`, `[10]`, `(10 Marks)`.
  - Sub-question detection: `1.`, `2.`, `(a)`, `(i)`.
  - Option normalization: converts `A/B/C/D`, `a/b/c/d`, `(A)/(B)/(C)/(D)`, `(a)/(b)/(c)/(d)`, `(1)/(2)/(3)/(4)` to standard `(1)`, `(2)`, `(3)`, `(4)`.
  - Automatic diagram placeholder detection for keywords: figure, diagram, map, outline map, graph, table.

### 2. Template Selection (3a vs 3b)
- **Decision:** If $> 50\%$ of detected questions are of type `MCQ` (carrying 4 options), select Template 3b (MCQ 2-column booklet format); otherwise select Template 3a (Theory paper).

### 3. Word 2007 Compatibility (.docx)
- **Decision:** Use `python-docx` augmented with direct `lxml.etree` OpenXML manipulation for page borders (`w:pgBorders`), headers/footers with page numbers, 2-column sections (`w:cols`), and table borders.
