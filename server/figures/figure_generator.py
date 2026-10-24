from typing import List, Dict, Any, Optional

def generate_timeline_svg(
    events: List[Dict[str, Any]],
    width: int = 560,
    height: int = 140
) -> str:
    """
    Renders clean black-and-white horizontal timeline for TIMELINE question types.
    Blanks are rendered as dotted/empty completion boxes.
    """
    n = len(events)
    if n == 0:
        return ""

    padding_x = 40
    step_x = (width - 2 * padding_x) / (n - 1 if n > 1 else 1)
    y_center = height // 2

    elements = []
    # Main horizontal axis
    elements.append(f'<line x1="{padding_x}" y1="{y_center}" x2="{width - padding_x}" y2="{y_center}" stroke="#1a1a1a" stroke-width="2.5" />')

    for i, ev in enumerate(events):
        x = padding_x + i * step_x
        year = ev.get("year", "")
        text = ev.get("text", "")
        is_blank = ev.get("blank", False)

        # Node dot
        elements.append(f'<circle cx="{x}" cy="{y_center}" r="5" fill="#1a1a1a" />')

        # Year label above
        elements.append(f'<text x="{x}" y="{y_center - 16}" text-anchor="middle" font-family="Times New Roman, serif" font-weight="bold" font-size="14" fill="#111">{year}</text>')

        # Text or Blank box below
        if is_blank:
            elements.append(f'<rect x="{x - 45}" y="{y_center + 12}" width="90" height="28" fill="#fff" stroke="#1a1a1a" stroke-width="1.5" stroke-dasharray="3,3" />')
            elements.append(f'<text x="{x}" y="{y_center + 30}" text-anchor="middle" font-family="monospace" font-size="10" fill="#999">[ _____ ]</text>')
        else:
            elements.append(f'<rect x="{x - 45}" y="{y_center + 12}" width="90" height="28" fill="#fbfaf7" stroke="#1a1a1a" stroke-width="1" />')
            elements.append(f'<text x="{x}" y="{y_center + 30}" text-anchor="middle" font-family="Times New Roman, serif" font-size="11" fill="#111">{text[:14]}</text>')

    svg_content = "\n  ".join(elements)
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#ffffff"/>
  {svg_content}
</svg>"""

def generate_concept_map_svg(
    root_title: str,
    branches: List[Dict[str, Any]],
    width: int = 560,
    height: int = 180
) -> str:
    """
    Renders clean tree / concept map flowchart for CONCEPT_MAP question types.
    """
    elements = []
    root_x = width // 2
    root_y = 35
    root_w = 140
    root_h = 36

    # Root Box
    elements.append(f'<rect x="{root_x - root_w//2}" y="{root_y - root_h//2}" width="{root_w}" height="{root_h}" fill="#f4f2ec" stroke="#1a1a1a" stroke-width="1.5" />')
    elements.append(f'<text x="{root_x}" y="{root_y + 4}" text-anchor="middle" font-family="Times New Roman, serif" font-weight="bold" font-size="13" fill="#111">{root_title}</text>')

    # Branches
    n = len(branches)
    if n > 0:
        padding_x = 35
        step_x = (width - 2 * padding_x) / (n - 1 if n > 1 else 1)
        branch_y = height - 45
        branch_w = 110
        branch_h = 40

        for i, b in enumerate(branches):
            bx = padding_x + i * step_x
            text = b.get("text", "")
            is_blank = b.get("blank", False) or not text.strip()

            # Connecting line from root to branch
            elements.append(f'<path d="M {root_x} {root_y + root_h//2} L {bx} {branch_y - branch_h//2}" stroke="#1a1a1a" stroke-width="1.2" fill="none" />')

            # Branch box
            if is_blank:
                elements.append(f'<rect x="{bx - branch_w//2}" y="{branch_y - branch_h//2}" width="{branch_w}" height="{branch_h}" fill="#fff" stroke="#1a1a1a" stroke-width="1.5" stroke-dasharray="4,3" />')
                elements.append(f'<text x="{bx}" y="{branch_y + 4}" text-anchor="middle" font-family="monospace" font-size="10" fill="#888">[ Complete ]</text>')
            else:
                elements.append(f'<rect x="{bx - branch_w//2}" y="{branch_y - branch_h//2}" width="{branch_w}" height="{branch_h}" fill="#fff" stroke="#1a1a1a" stroke-width="1" />')
                elements.append(f'<text x="{bx}" y="{branch_y + 4}" text-anchor="middle" font-family="Times New Roman, serif" font-size="11" fill="#111">{text}</text>')

    svg_content = "\n  ".join(elements)
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#ffffff"/>
  {svg_content}
</svg>"""
