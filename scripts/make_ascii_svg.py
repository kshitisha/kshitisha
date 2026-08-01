"""
Convert source-prepped.png to a self-typing ASCII portrait SVG.
Run locally whenever you update your photo.
"""
from PIL import Image
import numpy as np

COLS = 90
ROWS = 50
RAMP = " .`':-=+*cso#%@"
CHAR_W = 7.2
CHAR_H = 14
FONT_SIZE = 12
PAD_X = 10
PAD_Y = 18
FILL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
ANIM_DELAY_PER_ROW = 0.04  # seconds

img = Image.open("source-prepped.png").convert("L")
img = img.resize((COLS, ROWS), Image.LANCZOS)
pixels = np.array(img)

ascii_rows = []
for row in pixels:
    line = "".join(RAMP[int(px / 255 * (len(RAMP) - 1))] for px in row)
    ascii_rows.append(line)

SVG_W = int(COLS * CHAR_W + PAD_X * 2)
SVG_H = int(ROWS * CHAR_H + PAD_Y * 2)

lines = [
    f'<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}">',
    f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
    '<style>',
    f'text {{ font-family: "Courier New", Courier, monospace; font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; white-space: pre; }}',
]
for i in range(ROWS):
    delay = i * ANIM_DELAY_PER_ROW
    lines.append(f'.r{i} {{ animation: reveal 0.001s {delay:.3f}s forwards; opacity: 0; }}')
lines += ['@keyframes reveal { to { opacity: 1; } }', '</style>']

for i, row in enumerate(ascii_rows):
    y = PAD_Y + i * CHAR_H
    row_esc = row.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
    lines.append(f'<text class="r{i}" x="{PAD_X}" y="{y}">{row_esc}</text>')

lines.append('</svg>')
with open("ruru-ascii.svg", "w") as f:
    f.write('\n'.join(lines))
print(f"ruru-ascii.svg written ({SVG_W}x{SVG_H})")
