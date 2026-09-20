#!/usr/bin/env python3
"""
render_matrix_strip.py
Generates assets/matrix-strip.svg
A thin 880x46px horizontal strip of falling monochrome characters,
acting as a subtle ambient texture above the boot sequence.
Pure CSS keyframes, looping, semi-transparent. No em dashes anywhere.
"""

import os
import random

CHARS = "01ABCDEFabcdef0123456789#$%@!?><{}[]"
COLS = 55       # number of character columns across 880px
STRIP_W = 880
STRIP_H = 46
COL_W = STRIP_W / COLS

def make_col(i: int) -> str:
    # Each column: 2-4 stacked characters, random chars
    chars = [random.choice(CHARS) for _ in range(random.randint(2, 4))]
    y_start = random.randint(-30, 10)
    delay = round(random.uniform(0, 4.0), 2)
    duration = round(random.uniform(2.5, 5.5), 2)
    x = COL_W * i + COL_W * 0.5
    opacity = round(random.uniform(0.18, 0.42), 2)

    # Build a group that slides down and fades
    lines = []
    for j, ch in enumerate(chars):
        y = y_start + j * 13
        fade = max(0.05, opacity - j * 0.08)
        lines.append(
            f'<text x="{x:.1f}" y="{y}" class="mc" '
            f'style="opacity:{fade:.2f}; animation-delay:{delay}s; '
            f'animation-duration:{duration}s;">{ch}</text>'
        )
    return "\n    ".join(lines)

def generate() -> str:
    random.seed(42)   # deterministic so SVG is stable across runs
    col_elements = "\n    ".join(make_col(i) for i in range(COLS))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {STRIP_W} {STRIP_H}" width="{STRIP_W}" height="{STRIP_H}">
  <defs>
    <linearGradient id="mBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <clipPath id="mClip">
      <rect width="{STRIP_W}" height="{STRIP_H}"/>
    </clipPath>
  </defs>
  <style>
    @keyframes mFall {{
      0%   {{ transform: translateY(0px);   opacity: var(--op, 0.25); }}
      50%  {{ opacity: var(--op2, 0.40); }}
      100% {{ transform: translateY({STRIP_H + 20}px); opacity: 0; }}
    }}
    .mc {{
      font-family: "Fira Code", "SFMono-Regular", Consolas, monospace;
      font-size: 11px;
      fill: #39d353;
      animation: mFall linear infinite;
      will-change: transform, opacity;
    }}
  </style>
  <rect width="{STRIP_W}" height="{STRIP_H}" fill="url(#mBg)" rx="6"/>
  <rect width="{STRIP_W}" height="{STRIP_H}" fill="none" stroke="#21262d" stroke-width="1" rx="6"/>
  <g clip-path="url(#mClip)">
    {col_elements}
  </g>
</svg>"""

def main():
    os.makedirs("assets", exist_ok=True)
    svg = generate()
    with open("assets/matrix-strip.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated assets/matrix-strip.svg (880x46)")

if __name__ == "__main__":
    main()
