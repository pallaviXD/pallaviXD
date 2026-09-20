#!/usr/bin/env python3
"""
render_heatmap.py
Reads data/contributions.json and generates contrib-heatmap.svg
Features:
- Self-contained SVG with pure CSS keyframe animations
- Diagonal line-by-line slide-down on load (runs once, freezes)
- GitHub-green palette with rounded boxes
- Top terminal prompt bar
- Month and day labels
- Less -> More legend
- Detailed stats footer (total, active days, current streak, longest streak)
- Fixed width of 880px to align perfectly with bottom two columns (380 + 500)
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta

def generate_heatmap_svg(data: dict) -> str:
    days = data.get("days", [])
    if not days:
        raise ValueError("No days data found in contributions JSON.")

    # We need 53 columns x 7 rows.
    # GitHub's grid is arranged in columns (Sunday = 0 to Saturday = 6).
    # Group days into weeks.
    
    # Parse dates
    parsed_days = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        parsed_days.append({
            "date": d["date"],
            "dt": dt,
            "weekday": (dt.weekday() + 1) % 7, # Sunday = 0, Monday = 1, ..., Saturday = 6
            "level": d["level"],
            "count": d["count"]
        })
    
    # Organize into 53 weeks
    # Pad beginning so that the first day aligns to its weekday
    weeks = []
    current_week = [None] * 7
    
    first_day = parsed_days[0]
    first_weekday = first_day["weekday"]
    
    # Place days into weeks
    week_idx = 0
    day_in_week = first_weekday
    
    for d in parsed_days:
        if day_in_week == 7:
            weeks.append(current_week)
            current_week = [None] * 7
            day_in_week = 0
        current_week[day_in_week] = d
        day_in_week += 1
        
    if any(d is not None for d in current_week):
        weeks.append(current_week)
        
    # Limit or pad to exactly 53 weeks
    if len(weeks) > 53:
        weeks = weeks[-53:]
    elif len(weeks) < 53:
        weeks = [[None]*7 for _ in range(53 - len(weeks))] + weeks

    # Month labels calculation: track when month changes
    month_labels = []
    last_month = None
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for col_idx, week in enumerate(weeks):
        for day in week:
            if day:
                m = day["dt"].month
                if m != last_month:
                    last_month = m
                    month_labels.append((col_idx, month_names[m - 1]))
                break

    # Palette
    PALETTE = {
        0: "#161b22",  # Empty day
        1: "#0e4429",  # Level 1
        2: "#006d32",  # Level 2
        3: "#26a641",  # Level 3
        4: "#39d353",  # Level 4
    }
    BORDER_COLORS = {
        0: "rgba(255,255,255,0.04)",
        1: "rgba(0,0,0,0.15)",
        2: "rgba(0,0,0,0.15)",
        3: "rgba(0,0,0,0.15)",
        4: "rgba(0,0,0,0.15)",
    }

    # Layout dimensions (Width = 880px to align with 380px + 500px bottom columns)
    svg_width = 880
    svg_height = 224
    
    # Grid coordinates
    grid_start_x = 64
    grid_start_y = 74
    box_size = 11.2
    gap = 3.3
    
    # Generate Month XML
    month_svg = []
    for col_idx, name in month_labels:
        mx = grid_start_x + col_idx * (box_size + gap)
        month_svg.append(f'<text x="{mx:.1f}" y="{grid_start_y - 8}" class="month-label">{name}</text>')
        
    # Day labels (Mon, Wed, Fri correspond to row 1, 3, 5 in Sunday-first indexing)
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    day_svg = []
    for row_idx, label in day_labels:
        dy = grid_start_y + row_idx * (box_size + gap) + 9
        day_svg.append(f'<text x="{grid_start_x - 12}" y="{dy:.1f}" text-anchor="end" class="day-label">{label}</text>')
        
    # Generate Squares with diagonal slide-down animation
    rects_svg = []
    for col_idx in range(53):
        week = weeks[col_idx]
        for row_idx in range(7):
            d = week[row_idx]
            x = grid_start_x + col_idx * (box_size + gap)
            y = grid_start_y + row_idx * (box_size + gap)
            
            if d is None:
                continue
                
            level = d.get("level", 0)
            fill = PALETTE.get(level, PALETTE[0])
            stroke = BORDER_COLORS.get(level, "transparent")
            
            # Diagonal index: (col_idx + row_idx) gives waves sweeping top-left to bottom-right
            diag_index = col_idx + row_idx
            delay_ms = int(diag_index * 13) # 0 to ~780ms
            
            rect_xml = (
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_size:.1f}" height="{box_size:.1f}" '
                f'rx="2.5" ry="2.5" fill="{fill}" stroke="{stroke}" stroke-width="0.6" '
                f'class="cell" style="animation-delay: {delay_ms}ms;">'
                f'<title>{d["date"]}: {d["count"]} contributions</title>'
                f'</rect>'
            )
            rects_svg.append(rect_xml)

    # Legend coordinates (bottom right)
    legend_x = svg_width - 170
    legend_y = svg_height - 20
    legend_boxes = []
    for i in range(5):
        bx = legend_x + 36 + i * (10 + 3)
        legend_boxes.append(
            f'<rect x="{bx}" y="{legend_y - 8}" width="10" height="10" rx="2" ry="2" fill="{PALETTE[i]}" />'
        )
    legend_svg = (
        f'<g class="legend">'
        f'<text x="{legend_x + 30}" y="{legend_y}" text-anchor="end" class="legend-text">Less</text>'
        f'{"".join(legend_boxes)}'
        f'<text x="{legend_x + 36 + 5 * 13 + 6}" y="{legend_y}" text-anchor="start" class="legend-text">More</text>'
        f'</g>'
    )

    # Stats footer (bottom left)
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    active_days = data.get("active_days", 0)
    
    stats_y = svg_height - 20
    stats_svg = (
        f'<g class="stats">'
        f'<text x="24" y="{stats_y}" class="stat-item">'
        f'<tspan class="stat-value">{total_contribs}</tspan> <tspan class="stat-label">Contributions</tspan>'
        f'<tspan class="stat-dot"> · </tspan>'
        f'<tspan class="stat-value">{current_streak}d</tspan> <tspan class="stat-label">Current Streak</tspan>'
        f'<tspan class="stat-dot"> · </tspan>'
        f'<tspan class="stat-value">{longest_streak}d</tspan> <tspan class="stat-label">Longest Streak</tspan>'
        f'<tspan class="stat-dot"> · </tspan>'
        f'<tspan class="stat-value">{active_days}d</tspan> <tspan class="stat-label">Active Days</tspan>'
        f'</text>'
        f'</g>'
    )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
    <linearGradient id="promptGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58a6ff" />
      <stop offset="100%" stop-color="#39d353" />
    </linearGradient>
  </defs>

  <style>
    .terminal-bg {{
      fill: url(#bgGrad);
      stroke: #30363d;
      stroke-width: 1;
      rx: 8px;
    }}
    .header-bar {{
      fill: #161b22;
      stroke: #30363d;
      stroke-width: 1;
    }}
    .term-title {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Fira Code", monospace;
      font-size: 11px;
      fill: #8b949e;
      font-weight: 500;
    }}
    .term-prompt {{
      font-family: "Fira Code", "Courier New", monospace;
      font-size: 11.5px;
      font-weight: 600;
    }}
    .month-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10px;
      fill: #7d8590;
    }}
    .day-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9px;
      fill: #7d8590;
    }}
    .legend-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10px;
      fill: #7d8590;
    }}
    .stat-value {{
      font-family: "Fira Code", monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #58a6ff;
    }}
    .stat-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10.5px;
      fill: #8b949e;
    }}
    .stat-dot {{
      fill: #484f58;
      font-size: 11px;
    }}

    /* Diagonal line-by-line slide-down animation on load (runs once, freezes) */
    @keyframes diagSlide {{
      0% {{
        opacity: 0;
        transform: translateY(-8px);
      }}
      100% {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}

    .cell {{
      animation: diagSlide 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    @media (prefers-reduced-motion: reduce) {{
      .cell {{
        animation: none !important;
        opacity: 1 !important;
      }}
    }}
  </style>

  <!-- Container Box -->
  <rect x="0.5" y="0.5" width="{svg_width - 1}" height="{svg_height - 1}" rx="8" class="terminal-bg" />

  <!-- Terminal Window Top Bar -->
  <path d="M 0.5 8 A 7.5 7.5 0 0 1 8 0.5 L {svg_width - 8} 0.5 A 7.5 7.5 0 0 1 {svg_width - 0.5} 8 L {svg_width - 0.5} 32 L 0.5 32 Z" fill="#161b22" stroke="#30363d" stroke-width="1" />

  <!-- Window Control Buttons -->
  <circle cx="18" cy="16" r="5" fill="#ff5f56" />
  <circle cx="34" cy="16" r="5" fill="#ffbd2e" />
  <circle cx="50" cy="16" r="5" fill="#27c93f" />

  <!-- Terminal Prompt Command -->
  <text x="72" y="20" class="term-prompt">
    <tspan fill="#39d353">pallavi@github</tspan><tspan fill="#8b949e">:</tspan><tspan fill="#58a6ff">~</tspan><tspan fill="#e6edf3">$ fetch --contributions --timeline=53w</tspan>
  </text>

  <!-- Month Labels -->
  <g>
    {"".join(month_svg)}
  </g>

  <!-- Day Labels -->
  <g>
    {"".join(day_svg)}
  </g>

  <!-- 53x7 Contribution Grid -->
  <g>
    {"".join(rects_svg)}
  </g>

  <!-- Legend -->
  {legend_svg}

  <!-- Stats Footer -->
  {stats_svg}
</svg>"""
    return svg_content

def main():
    parser = argparse.ArgumentParser(description="Render contributions heatmap SVG")
    parser.add_argument("--input", default="data/contributions.json", help="Path to contributions JSON")
    parser.add_argument("--output", default="contrib-heatmap.svg", help="Path to output SVG")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} does not exist. Run fetch_contributions.py first.", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    svg = generate_heatmap_svg(data)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Successfully generated {args.output} (width: 880px)")

if __name__ == "__main__":
    main()
