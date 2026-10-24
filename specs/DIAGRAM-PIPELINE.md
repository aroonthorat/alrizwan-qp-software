# Diagram Pipeline — Accuracy First, No Retries

Read with `SOFTWARE-PLAN.md` (§3 step 7, §4 routing).

## Models

| Task | Route key | Model | Price (Oct 2026) |
|---|---|---|---|
| Read, tag, extract labels, rate complexity | `diagram_tag` | Gemini 3.8 Flash (vision) | ≈ ₹0.10 |
| Redraw simple diagram | `diagram_redraw` | Nano Banana 2.1, 2K | $0.0504 (batch $0.025) |
| Redraw complex diagram (maps, biology, circuits) | `diagram_redraw_complex` | Nano Banana Pro, 2K | $0.134 |

Do not use cheaper unverified models; one retry costs more than the saving.
Confirm prices on Google's official pricing page before launch.

## Flow

1. Teacher uploads/crops a diagram → free code cleanup (crop, grayscale, contrast).
2. `diagram_tag` returns JSON: `class, subject, chapter, tags[], labels[{text, x, y}], complexity: simple|complex, needs_redraw: bool`.
3. If `needs_redraw` is false → use the cleaned scan. No image model call.
4. Else route by `complexity` to `diagram_redraw` or `diagram_redraw_complex` with the fixed prompt below.
5. Code overlays labels / A-B-C markers from step 2 (correct language and font, never AI-drawn text).
6. Teacher approves once → saved to `diagrams` table. Never generated again.

## Fixed redraw prompt

> Redraw this exact diagram as clean black line art on a white background. Keep every shape,
> proportion and position identical. Remove all text, numbers and labels. No shading, no colour,
> no added elements.

## Cost rules

- Output 2K, black and white only.
- Bulk textbook import → Batch API (50% off), run overnight.
- Cache by image hash; same image never sent twice.
- Count each redraw in `ai_log` against the monthly cap.

Estimate: 500 diagrams (80% simple, 20% complex) in batch ≈ ₹2,100 one time.
