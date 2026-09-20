#!/usr/bin/env python3
"""
render_infocard.py
Generates assets/info-card.svg
Features:
- Self-contained SVG with pure CSS keyframes animation
- Neofetch-style terminal panel with titlebar and color palette bar
- Fields: Now, Prev, Stack, Highlights
- Staggered line fade/slide-in animation on load, print-once-and-freeze
- Fixed width: 500px, height: 490px (matching avi-ascii.svg)
"""

import argparse
import os

def generate_infocard_svg() -> str:
    svg_width = 500
    svg_height = 490

    # Color palette bar (8 neofetch terminal color blocks)
    colors = ["#21262d", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc"]
    color_rects = []
    bar_start_x = 32
    bar_y = 442
    rect_w = 20
    rect_h = 10
    for i, c in enumerate(colors):
        rx = bar_start_x + i * (rect_w + 4)
        color_rects.append(f'<rect x="{rx}" y="{bar_y}" width="{rect_w}" height="{rect_h}" rx="2" fill="{c}" />')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <defs>
    <linearGradient id="cardBgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
  </defs>

  <style>
    .card-bg {{
      fill: url(#cardBgGrad);
      stroke: #30363d;
      stroke-width: 1;
      rx: 8px;
    }}
    .term-prompt {{
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 11.5px;
      font-weight: 600;
    }}
    .mono-text {{
      font-family: "Fira Code", "SFMono-Regular", Consolas, Menlo, monospace;
    }}
    .sys-user {{
      font-size: 13.5px;
      font-weight: 700;
      fill: #58a6ff;
    }}
    .sys-host {{
      font-size: 13.5px;
      font-weight: 700;
      fill: #39d353;
    }}
    .sys-separator {{
      font-size: 11px;
      fill: #484f58;
    }}
    .key-label {{
      font-size: 11.5px;
      font-weight: 700;
      fill: #e3b341;
    }}
    .val-text {{
      font-size: 11.5px;
      fill: #e6edf3;
      font-weight: 500;
    }}
    .val-subtext {{
      font-size: 10.5px;
      fill: #8b949e;
    }}
    .val-tag {{
      font-size: 10px;
      fill: #58a6ff;
    }}
    .bullet {{
      fill: #3fb950;
      font-weight: bold;
    }}

    /* Staggered fade/slide-in animation (runs once, freezes) */
    @keyframes lineFadeIn {{
      0% {{
        opacity: 0;
        transform: translateY(6px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}

    .stagger-line {{
      opacity: 0;
      animation: lineFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      will-change: opacity, transform;
    }}

    .delay-0 {{ animation-delay: 80ms; }}
    .delay-1 {{ animation-delay: 180ms; }}
    .delay-2 {{ animation-delay: 280ms; }}
    .delay-3 {{ animation-delay: 400ms; }}
    .delay-4 {{ animation-delay: 520ms; }}
    .delay-5 {{ animation-delay: 640ms; }}
    .delay-6 {{ animation-delay: 760ms; }}
    .delay-7 {{ animation-delay: 880ms; }}
  </style>

  <!-- Container Box -->
  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="8" class="card-bg" />

  <!-- Terminal Window Top Bar -->
  <path d="M 0.5 8 A 7.5 7.5 0 0 1 8 0.5 L {svg_width - 8} 0.5 A 7.5 7.5 0 0 1 {svg_width - 0.5} 8 L {svg_width - 0.5} 32 L 0.5 32 Z" fill="#161b22" stroke="#30363d" stroke-width="1" />

  <!-- Window Control Buttons -->
  <circle cx="18" cy="16" r="5" fill="#ff5f56" />
  <circle cx="34" cy="16" r="5" fill="#ffbd2e" />
  <circle cx="50" cy="16" r="5" fill="#27c93f" />

  <!-- Terminal Prompt Command -->
  <text x="72" y="20" class="term-prompt">
    <tspan fill="#39d353">pallavi@DESKTOP</tspan><tspan fill="#8b949e">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#e6edf3">$ neofetch --profile</tspan>
  </text>

  <!-- Content Body -->
  <g class="mono-text">
    <!-- Header: pallavi@portfolio -->
    <g class="stagger-line delay-0">
      <text x="32" y="62">
        <tspan class="sys-user">pallavi</tspan><tspan fill="#8b949e">@</tspan><tspan class="sys-host">DESKTOP</tspan>
      </text>
      <text x="32" y="76" class="sys-separator">-------------------------------------------------</text>
    </g>

    <!-- Field 1: NOW -->
    <g class="stagger-line delay-1">
      <text x="32" y="104">
        <tspan class="key-label">Now      </tspan>
        <tspan fill="#8b949e">› </tspan>
        <tspan class="val-text">Backend Developer </tspan>
        <tspan fill="#79c0ff">@ One Tappe</tspan>
      </text>
      <text x="108" y="122" class="val-subtext">↳ Node.js/FastAPI · RAG systems · AI/LLM features</text>
    </g>

    <!-- Field 2: PREV -->
    <g class="stagger-line delay-2">
      <text x="32" y="152">
        <tspan class="key-label">Prev     </tspan>
        <tspan fill="#8b949e">› </tspan>
        <tspan class="val-text">Technical Writer </tspan>
        <tspan fill="#d2a8ff">@ Kahana</tspan>
        <tspan class="val-subtext"> (security docs)</tspan>
      </text>
      <text x="108" y="170" class="val-subtext">↳ Blog writer @ Axeploit (cybersecurity research)</text>
    </g>

    <!-- Field 3: STACK -->
    <g class="stagger-line delay-3">
      <text x="32" y="200">
        <tspan class="key-label">Stack    </tspan>
        <tspan fill="#8b949e">› </tspan>
        <tspan class="val-text">React · Next.js · Node.js · FastAPI</tspan>
      </text>
      <text x="108" y="218" class="val-text">TypeScript · Docker · FAISS/RAG</text>
      <text x="108" y="236" class="val-tag">LLM Orchestration: Groq · Gemini · LangChain</text>
    </g>

    <!-- Field 4: HIGHLIGHTS -->
    <g class="stagger-line delay-4">
      <text x="32" y="266">
        <tspan class="key-label">Highlights </tspan>
        <tspan fill="#8b949e">›</tspan>
      </text>
    </g>

    <g class="stagger-line delay-5">
      <!-- Item 1: SIH -->
      <text x="44" y="290">
        <tspan class="bullet">✦ </tspan>
        <tspan class="val-text" font-weight="600">SIH 2026 Grand Finalist </tspan>
        <tspan class="val-tag">(Top 50/3500+)</tspan>
      </text>
      <text x="60" y="306" class="val-subtext">SENTRA — AI Real-Time UPI Fraud Prevention</text>
    </g>

    <g class="stagger-line delay-6">
      <!-- Item 2: HACKHAZARDS & Luminix -->
      <text x="44" y="332">
        <tspan class="bullet">✦ </tspan>
        <tspan class="val-text" font-weight="600">HACKHAZARDS '26 Top 100 &amp; Luminix '26 Runner-Up</tspan>
      </text>
      <text x="60" y="348" class="val-subtext">UnifyTalk — AI-powered accessibility platform</text>

      <!-- Item 3: GSSoC -->
      <text x="44" y="374">
        <tspan class="bullet">✦ </tspan>
        <tspan class="val-text" font-weight="600">GSSoC Project Admin </tspan>
        <tspan class="val-tag">&amp; Campus Ambassador</tspan>
      </text>
      <text x="60" y="390" class="val-subtext">Admin for NutriMind-AI &amp; RepoScout repositories</text>
    </g>

    <!-- Color Palette Blocks -->
    <g class="stagger-line delay-7">
      <text x="32" y="426" class="val-subtext" font-size="10px">SYSTEM PALETTE</text>
      {"".join(color_rects)}
    </g>
  </g>
</svg>"""
    return svg_content

def main():
    parser = argparse.ArgumentParser(description="Render neofetch info card SVG")
    parser.add_argument("--output", default="assets/info-card.svg", help="Output SVG path")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    svg = generate_infocard_svg()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Successfully generated {args.output} (width: 500px, height: 490px)")

if __name__ == "__main__":
    main()
