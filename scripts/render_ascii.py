#!/usr/bin/env python3
"""
render_ascii.py
Converts a preprocessed portrait into an animated monochrome ASCII SVG.
Features:
- Density ramp brightness mapping
- Row-by-row typewriter wipe animation (CSS keyframes + SMIL fallback)
- Single light-gray fill (#c9d1d9) on terminal dark theme
- Print-once-and-freeze (no looping)
- Fixed dimensions: width 380px, height 490px (matching info-card.svg)
"""

import argparse
import html
import os
import sys
import numpy as np
from PIL import Image

# Ramp from light to dense:
# Inverted: 255 (white bg) -> ' ', 0 (dark subject) -> dense chars
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

def image_to_ascii(img: Image.Image, num_cols: int = 50, invert: bool = True) -> list[str]:
    # Aspect ratio adjustment: monospace font height is roughly 1.7x width
    char_aspect = 0.58
    w, h = img.size
    
    # Target rows between 34 and 38 to fill the 490px height
    target_rows = 36
    num_rows = target_rows
    num_cols = int((w / h) * (num_rows / char_aspect))
    if num_cols < 44:
        num_cols = 44
    elif num_cols > 54:
        num_cols = 54

    resized = img.resize((num_cols, num_rows), Image.Resampling.LANCZOS)
    gray = resized.convert("L")
    pixels = np.array(gray)

    ramp_chars = list(RAMP)
    ramp_len = len(ramp_chars)

    lines = []
    for row in pixels:
        line_chars = []
        for val in row:
            if invert:
                # White (255) -> 0 index (space), Dark (0) -> max index (@)
                idx = int(((255 - val) / 255.0) * (ramp_len - 1))
            else:
                idx = int((val / 255.0) * (ramp_len - 1))
            line_chars.append(ramp_chars[idx])
        lines.append("".join(line_chars))

    return lines

def generate_ascii_svg(lines: list[str], output_width=380, output_height=490) -> str:
    num_rows = len(lines)
    
    # Coordinates layout - nicely centered between top bar (32px) and bottom (475px)
    top_bar_height = 32
    margin_bottom = 20
    avail_height = output_height - top_bar_height - margin_bottom
    
    line_height = avail_height / (num_rows + 1)
    font_size = min(line_height * 0.78, 8.5)
    content_top = top_bar_height + (avail_height - (num_rows * line_height)) / 2 + 10

    # Stagger delay per row: 28ms per row gives a snappy, fluid typewriter wipe
    row_delay_ms = 28

    rows_xml = []
    for i, line in enumerate(lines):
        y = content_top + (i + 1) * line_height
        delay_sec = (i * row_delay_ms) / 1000.0
        escaped_text = html.escape(line)
        
        # Dual-layer animation: CSS keyframes + SMIL <animate> tag
        row_str = (
            f'<text x="{output_width / 2:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'class="ascii-row" style="animation-delay: {int(i * row_delay_ms)}ms;" xml:space="preserve">'
            f'{escaped_text}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.05s" begin="{delay_sec:.3f}s" fill="freeze" />'
            f'</text>'
        )
        rows_xml.append(row_str)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {output_width} {output_height}" width="{output_width}" height="{output_height}">
  <defs>
    <linearGradient id="aviBgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
  </defs>

  <style>
    .terminal-bg {{
      fill: url(#aviBgGrad);
      stroke: #30363d;
      stroke-width: 1;
      rx: 8px;
    }}
    .term-prompt {{
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 11.5px;
      font-weight: 600;
    }}
    
    /* Typewriter row-by-row wipe animation (runs once, freezes) */
    @keyframes typeWipe {{
      0% {{
        opacity: 0;
        transform: translateY(2px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}

    .ascii-row {{
      font-family: "Fira Code", "SFMono-Regular", Consolas, "Courier New", monospace;
      font-size: {font_size:.1f}px;
      letter-spacing: 1.4px;
      fill: #c9d1d9;
      opacity: 0;
      animation: typeWipe 0.08s ease-out forwards;
      will-change: opacity, transform;
    }}
  </style>

  <!-- Container Box -->
  <rect x="0.5" y="0.5" width="{output_width - 1}" height="{output_height - 1}" rx="8" class="terminal-bg" />

  <!-- Terminal Window Top Bar -->
  <path d="M 0.5 8 A 7.5 7.5 0 0 1 8 0.5 L {output_width - 8} 0.5 A 7.5 7.5 0 0 1 {output_width - 0.5} 8 L {output_width - 0.5} 32 L 0.5 32 Z" fill="#161b22" stroke="#30363d" stroke-width="1" />

  <!-- Window Control Buttons -->
  <circle cx="18" cy="16" r="5" fill="#ff5f56" />
  <circle cx="34" cy="16" r="5" fill="#ffbd2e" />
  <circle cx="50" cy="16" r="5" fill="#27c93f" />

  <!-- Terminal Prompt Command -->
  <text x="72" y="20" class="term-prompt">
    <tspan fill="#39d353">pallavi@DESKTOP</tspan><tspan fill="#8b949e">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#e6edf3">$ cat avatar.txt</tspan>
  </text>

  <!-- ASCII Lines -->
  <g id="ascii-art">
    {"".join(rows_xml)}
  </g>
</svg>"""
    return svg_content

def main():
    parser = argparse.ArgumentParser(description="Render ASCII portrait to animated SVG")
    parser.add_argument("--input", default="assets/prepped_portrait.png", help="Path to input image")
    parser.add_argument("--fallback", default="assets/input_photo.png", help="Fallback input image")
    parser.add_argument("--output", default="assets/avi-ascii.svg", help="Path to output SVG")
    parser.add_argument("--cols", type=int, default=48, help="Number of ASCII character columns")
    parser.add_argument("--no-invert", action="store_true", help="Disable brightness inversion")
    args = parser.parse_args()

    input_file = args.input
    if not os.path.exists(input_file):
        if os.path.exists(args.fallback):
            input_file = args.fallback
        else:
            print(f"Error: Neither {args.input} nor {args.fallback} found.", file=sys.stderr)
            sys.exit(1)

    print(f"Loading image from {input_file}...")
    img = Image.open(input_file)
    lines = image_to_ascii(img, num_cols=args.cols, invert=not args.no_invert)
    print(f"Generated {len(lines)} rows of ASCII.")

    svg = generate_ascii_svg(lines)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Successfully generated {args.output} (380x490)")

if __name__ == "__main__":
    main()
