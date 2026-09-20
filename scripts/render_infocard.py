#!/usr/bin/env python3
"""
render_infocard.py (refactored)
Generates assets/info-card.svg
Full-width 880x240px neofetch-style terminal panel. No em dashes anywhere.
Staggered fade/slide-in per field line, prints once and freezes.
"""

import os

SVG_W = 880
SVG_H = 240
TOP_BAR = 32
STAGGER = 160  # ms between each line

OK_COLOR   = "#3fb950"
KEY_COLOR  = "#e3b341"
VAL_COLOR  = "#e6edf3"
DIM_COLOR  = "#8b949e"
BLUE_COLOR = "#58a6ff"
PUR_COLOR  = "#d2a8ff"
CYAN_COLOR = "#39c5cf"

FIELDS = [
    # (key_text, value_parts) where value_parts is list of (text, color)
    ("identity",    [("final-year ISE student, backend engineer aiming toward ai/llm systems", VAL_COLOR)]),
    ("location",    [("bengaluru, india", DIM_COLOR)]),
    ("stack",       [("react, next.js, node.js, fastapi, typescript, docker, rag/faiss, groq, gemini", VAL_COLOR)]),
    ("highlights",  [("sih 2026 grand finalist, top 50 of 3500+ teams (sentra, upi fraud prevention)", VAL_COLOR)]),
    ("",            [("two hackathon podium finishes: unifytalk, accessibility app for deaf, mute, and blind users", DIM_COLOR)]),
    ("open-source", [("gssoc project admin: nutrimind-ai, reposcout", DIM_COLOR)]),
]

# Palette blocks
PALETTE = ["#21262d","#ff7b72","#3fb950","#d29922","#58a6ff","#bc8cff","#39c5cf","#f0f6fc"]

def make_field_line(idx: int, key: str, value_parts) -> str:
    y = TOP_BAR + 28 + idx * 26
    delay = idx * STAGGER

    # If value_parts is a plain string, wrap it
    if isinstance(value_parts, str):
        value_parts = [(value_parts, DIM_COLOR)]

    tspans = []
    if key:
        key_padded = key.ljust(12)
        tspans.append(f'<tspan fill="{KEY_COLOR}" font-weight="bold">{key_padded} </tspan>')
        tspans.append(f'<tspan fill="#484f58">: </tspan>')
    else:
        # continuation indent
        tspans.append(f'<tspan fill="{DIM_COLOR}">{"":>15}</tspan>')

    for text, color in value_parts:
        tspans.append(f'<tspan fill="{color}">{text}</tspan>')

    tspan_str = "".join(tspans)
    return (
        f'  <text x="24" y="{y}" class="info-line" style="animation-delay:{delay}ms;">'
        f'{tspan_str}'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.1s" begin="{delay}ms" fill="freeze"/>'
        f'</text>'
    )

def generate() -> str:
    field_lines = [make_field_line(i, k, v) for i, (k, v) in enumerate(FIELDS)]

    # Color palette row
    palette_y = TOP_BAR + 28 + len(FIELDS) * 26 + 4
    palette_delay = len(FIELDS) * STAGGER
    pal_rects = []
    for j, c in enumerate(PALETTE):
        rx = 24 + j * 24
        pal_rects.append(f'<rect x="{rx}" y="{palette_y - 10}" width="18" height="10" rx="2" fill="{c}"/>')
    pal_group = (
        f'  <g opacity="0" style="animation-delay:{palette_delay}ms;" class="info-line">'
        f'\n    <text x="24" y="{palette_y - 14}" fill="{DIM_COLOR}" font-size="9px" '
        f'font-family="\'Fira Code\',monospace">SYSTEM PALETTE</text>'
        f'\n    {"".join(pal_rects)}'
        f'\n    <animate attributeName="opacity" from="0" to="1" dur="0.1s" begin="{palette_delay}ms" fill="freeze"/>'
        f'\n  </g>'
    )

    # User header: pallavi@DESKTOP
    header_delay = 0

    fields_svg = "\n".join(field_lines)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">
  <defs>
    <linearGradient id="icBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
  </defs>
  <style>
    @keyframes slideFade {{
      0%   {{ opacity: 0; transform: translateY(5px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .info-line {{
      font-family: "Fira Code", "SFMono-Regular", Consolas, "Courier New", monospace;
      font-size: 12px;
      opacity: 0;
      animation: slideFade 0.35s cubic-bezier(0.16,1,0.3,1) forwards;
      will-change: opacity, transform;
    }}
    .term-prompt {{
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 11.5px;
      font-weight: 600;
    }}
  </style>

  <!-- Container -->
  <rect x="0.5" y="0.5" width="{SVG_W-1}" height="{SVG_H-1}" rx="8" fill="url(#icBg)" stroke="#30363d" stroke-width="1"/>

  <!-- Title bar -->
  <path d="M 0.5 8 A 7.5 7.5 0 0 1 8 0.5 L {SVG_W-8} 0.5 A 7.5 7.5 0 0 1 {SVG_W-0.5} 8 L {SVG_W-0.5} 32 L 0.5 32 Z"
        fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <circle cx="18" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="34" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>
  <text x="70" y="20.5" class="term-prompt">
    <tspan fill="{OK_COLOR}">pallavi@DESKTOP</tspan><tspan fill="#484f58">:</tspan><tspan fill="{BLUE_COLOR}">~</tspan><tspan fill="#e6edf3">$ neofetch --profile</tspan>
  </text>
  <line x1="0" y1="32" x2="{SVG_W}" y2="32" stroke="#21262d" stroke-width="1"/>

  <!-- User identity header -->
  <text x="24" y="{TOP_BAR + 20}" font-family="\'Fira Code\',monospace" font-size="14px" font-weight="bold" opacity="0"
        style="animation-delay:0ms;" class="info-line">
    <tspan fill="{BLUE_COLOR}">pallavi</tspan><tspan fill="{DIM_COLOR}">@</tspan><tspan fill="{OK_COLOR}">DESKTOP</tspan>
    <animate attributeName="opacity" from="0" to="1" dur="0.1s" begin="0ms" fill="freeze"/>
  </text>

  <!-- Field lines -->
{fields_svg}

  <!-- Palette group -->
{pal_group}
</svg>"""

def main():
    os.makedirs("assets", exist_ok=True)
    svg = generate()
    with open("assets/info-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated assets/info-card.svg (880x240)")

if __name__ == "__main__":
    main()
