#!/usr/bin/env python3
"""
render_boot_sequence.py
Generates assets/boot-sequence.svg
A fake terminal boot log that types itself line by line with a blinking
cursor, prints once and freezes. No em dashes anywhere.
Width: 880px, Height: 240px.
"""

import html
import os

# Boot log lines. No em dashes. Use colons, commas, periods only.
BOOT_LINES = [
    ("ok",     "loading module: backend-engineering"),
    ("ok",     "loading module: rag-pipelines"),
    ("ok",     "loading module: llm-systems"),
    ("wait",   "compiling ambition: ai/llm engineer : 73%"),
    ("ok",     "hackathons indexed: 3 podium finishes"),
    ("ok",     "open-source: gssoc project admin"),
    ("ok",     "status: still building"),
]

SVG_W = 880
SVG_H = 240
TOP_BAR = 32
LINE_H  = 22      # px per line
START_Y = TOP_BAR + 26
STAGGER = 380     # ms between each line appearing

OK_COLOR    = "#3fb950"
WAIT_COLOR  = "#e3b341"
DIM_COLOR   = "#8b949e"
TEXT_COLOR  = "#e6edf3"
CURSOR_COLOR = "#58a6ff"

def ok_badge(kind: str) -> str:
    if kind == "ok":
        return f'<tspan fill="{OK_COLOR}" font-weight="bold">[ OK ]</tspan>'
    return f'<tspan fill="{WAIT_COLOR}" font-weight="bold">[....]</tspan>'

def generate() -> str:
    # Build the per-line SVG text elements
    line_els = []
    for i, (kind, text) in enumerate(BOOT_LINES):
        y = START_Y + i * LINE_H
        delay_ms = i * STAGGER
        badge = ok_badge(kind)
        escaped = html.escape(text)

        line_els.append(
            f'  <text x="28" y="{y}" class="boot-line" style="animation-delay:{delay_ms}ms;">'
            f'{badge} <tspan fill="{TEXT_COLOR}">{escaped}</tspan>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.08s" '
            f'begin="{delay_ms}ms" fill="freeze"/>'
            f'</text>'
        )

    # Blinking cursor appears after last line
    last_y = START_Y + len(BOOT_LINES) * LINE_H
    cursor_delay = len(BOOT_LINES) * STAGGER

    line_els.append(
        f'  <text x="28" y="{last_y}" class="boot-line" style="animation-delay:{cursor_delay}ms;">'
        f'<tspan fill="{OK_COLOR}" font-weight="bold">[done]</tspan> '
        f'<tspan fill="{DIM_COLOR}">pallavi@DESKTOP:~$</tspan> '
        f'<tspan fill="{CURSOR_COLOR}" class="cursor">|</tspan>'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.08s" '
        f'begin="{cursor_delay}ms" fill="freeze"/>'
        f'</text>'
    )

    lines_svg = "\n".join(line_els)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">
  <defs>
    <linearGradient id="bsBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
  </defs>
  <style>
    /* Print once and freeze */
    @keyframes bootAppear {{
      from {{ opacity: 0; }}
      to   {{ opacity: 1; }}
    }}

    .boot-line {{
      font-family: "Fira Code", "SFMono-Regular", Consolas, "Courier New", monospace;
      font-size: 13px;
      animation: bootAppear 0.08s ease both;
    }}

    /* Blinking cursor blinks after it appears */
    @keyframes blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    .cursor {{
      animation: blink 1s step-end infinite;
      animation-delay: {len(BOOT_LINES) * STAGGER + 200}ms;
    }}
    .term-prompt {{
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 11.5px;
      font-weight: 600;
    }}
    @media (prefers-reduced-motion: reduce) {{
      .boot-line, .cursor {{
        animation: none !important;
        opacity: 1 !important;
      }}
    }}
  </style>

  <!-- Container -->
  <rect x="0.5" y="0.5" width="{SVG_W-1}" height="{SVG_H-1}" rx="8" fill="url(#bsBg)" stroke="#30363d" stroke-width="1"/>

  <!-- Title bar -->
  <path d="M 0.5 8 A 7.5 7.5 0 0 1 8 0.5 L {SVG_W-8} 0.5 A 7.5 7.5 0 0 1 {SVG_W-0.5} 8 L {SVG_W-0.5} 32 L 0.5 32 Z"
        fill="#161b22" stroke="#30363d" stroke-width="1"/>

  <!-- Window control dots -->
  <circle cx="18" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="34" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>

  <!-- Prompt in title bar -->
  <text x="70" y="20.5" class="term-prompt">
    <tspan fill="{OK_COLOR}">pallavi@DESKTOP</tspan><tspan fill="#484f58">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#e6edf3">$ ./initialize_pallaviXD.sh</tspan>
  </text>

  <!-- Divider line -->
  <line x1="0" y1="32" x2="{SVG_W}" y2="32" stroke="#21262d" stroke-width="1"/>

{lines_svg}
</svg>"""

def main():
    os.makedirs("assets", exist_ok=True)
    svg = generate()
    with open("assets/boot-sequence.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated assets/boot-sequence.svg (880x240)")

if __name__ == "__main__":
    main()
