"""
Placeholder for code-drawn SVG generators (timelines, concept maps, tables) scheduled for Phase 4.
"""

def generate_placeholder_svg(title: str, width: int = 280, height: int = 175) -> str:
    return f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <pattern id="hatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="12" stroke="#e0ded6" stroke-width="4" />
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="#fbfaf7" stroke="#1a1a1a" stroke-width="1"/>
  <rect width="100%" height="100%" fill="url(#hatch)"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="monospace" font-size="11" fill="#666666">{title}</text>
</svg>"""
