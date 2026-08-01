"""
Render contributions.json as an animated SVG heatmap.
Diagonal slide-in animation, freezes after one play.
"""
import json
from pathlib import Path
from datetime import datetime, date, timedelta

DATA = Path("data/contributions.json")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BOX = 13
GAP = 3
STEP = BOX + GAP
WEEKS = 53
DAYS = 7
PAD_L = 36   # left padding for day labels
PAD_T = 32   # top padding for month labels
PAD_R = 20
PAD_B = 56   # bottom for legend + stats
BG = "#0d1117"
TEXT = "#8b949e"
FONT = '"Segoe UI", system-ui, sans-serif'

W = PAD_L + WEEKS * STEP + PAD_R
H = PAD_T + DAYS * STEP + PAD_B

DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]

def level_color(lvl):
    return PALETTE[min(lvl, len(PALETTE)-1)]

def render(data):
    days = data["days"]
    # Build week grid
    # Find the Sunday that starts the first week
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    # Pad to previous Sunday
    offset = first_date.weekday() + 1  # Mon=0, so Sun = 6 -> offset=0... adjust
    # GitHub uses Sun=0
    dow = (first_date.weekday() + 1) % 7  # Sun=0
    grid_start = first_date - timedelta(days=dow)

    day_map = {d["date"]: d for d in days}

    svg = []
    svg.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">')
    svg.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    svg.append(f'<style>text{{font-family:{FONT};fill:{TEXT};font-size:11px;}}</style>')

    # Day-of-week labels
    for i, label in enumerate(DAY_LABELS):
        if label:
            y = PAD_T + i * STEP + BOX - 2
            svg.append(f'<text x="0" y="{y}" font-size="10">{label}</text>')

    # Month labels
    prev_month = None
    for w in range(WEEKS):
        d = grid_start + timedelta(weeks=w)
        m = d.strftime("%b")
        if m != prev_month:
            x = PAD_L + w * STEP
            svg.append(f'<text x="{x}" y="{PAD_T - 6}" font-size="10">{m}</text>')
            prev_month = m

    # Boxes with diagonal stagger animation
    total_diags = WEEKS + DAYS - 1
    ANIM_TOTAL = 2.0  # seconds for full reveal

    for w in range(WEEKS):
        for d in range(DAYS):
            cur = grid_start + timedelta(weeks=w, days=d)
            date_str = cur.isoformat()
            entry = day_map.get(date_str)
            lvl = entry["level"] if entry else 0
            color = level_color(lvl)
            count = entry["count"] if entry else 0

            x = PAD_L + w * STEP
            y = PAD_T + d * STEP

            diag = w + d
            delay = (diag / total_diags) * ANIM_TOTAL

            svg.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" ry="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" values="0;1" dur="0.001s" '
                f'begin="{delay:.3f}s" fill="freeze"/>'
                f'</rect>'
            )

    # Legend
    legend_y = H - 22
    svg.append(f'<text x="{PAD_L}" y="{legend_y + 10}">Less</text>')
    lx = PAD_L + 34
    for i in range(6):
        svg.append(f'<rect x="{lx + i*17}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{PALETTE[i]}"/>')
    svg.append(f'<text x="{lx + 6*17 + 4}" y="{legend_y + 10}">More</text>')

    # Stats footer
    stats_y = H - 40
    total = data["total"]
    streak = data["current_streak"]
    longest = data["longest_streak"]
    best = data["best_day"]
    svg.append(f'<text x="{PAD_L}" y="{stats_y}" font-size="12" fill="#c9d1d9">'
               f'{total:,} contributions in the last year  ·  '
               f'streak: {streak}d  ·  longest: {longest}d  ·  '
               f'best: {best["count"]} ({best["date"]})</text>')

    svg.append('</svg>')
    return '\n'.join(svg)

if __name__ == "__main__":
    with open(DATA) as f:
        data = json.load(f)
    svg = render(data)
    Path("contrib-heatmap.svg").write_text(svg)
    print(f"Heatmap SVG written: {W}x{H}px")
