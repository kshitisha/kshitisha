"""
Convert source-prepped.png to a self-typing ASCII portrait SVG.
Automatically crops empty rows and preserves aspect ratio.
"""

from PIL import Image
import numpy as np

COLS = 90
MAX_ROWS = 60

RAMP = " .`':-=+*cso#%@"

CHAR_W = 7.2
CHAR_H = 14
FONT_SIZE = 12

PAD_X = 10
PAD_Y = 18

FILL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"

ANIM_DELAY_PER_ROW = 0.045




img = Image.open("source-prepped.png").convert("L")

# Preserve aspect ratio
w, h = img.size
new_h = int(h * COLS / w)

if new_h > MAX_ROWS:
    scale = MAX_ROWS / new_h
    new_h = MAX_ROWS
    new_w = int(COLS * scale)
else:
    new_w = COLS

img = img.resize((new_w, new_h), Image.LANCZOS)

# Center on white canvas
canvas = Image.new("L", (COLS, MAX_ROWS), 255)

offset_x = (COLS - new_w) // 2
offset_y = (MAX_ROWS - new_h) // 2

canvas.paste(img, (offset_x, offset_y))

pixels = np.array(canvas)



ascii_rows = []

for row in pixels:
    line = "".join(
        RAMP[int(px / 255 * (len(RAMP) - 1))]
        for px in row
    )
    ascii_rows.append(line)



def is_blank(line):
    useful = line.translate(str.maketrans("", "", " .`':"))
    return len(useful) < 10


while ascii_rows and is_blank(ascii_rows[0]):
    ascii_rows.pop(0)

while ascii_rows and is_blank(ascii_rows[-1]):
    ascii_rows.pop()

ROWS = len(ascii_rows)

SVG_W = int(COLS * CHAR_W + PAD_X * 2)
SVG_H = int((ROWS - 1) * CHAR_H + PAD_Y * 2)



lines = [
    f'<svg viewBox="0 0 {SVG_W} {SVG_H}" xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}">',
    f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>',
    "<style>",
    f'text {{ font-family: "Courier New", Courier, monospace; font-size:{FONT_SIZE}px; fill:{FILL_COLOR}; white-space:pre; }}'
]

for i in range(ROWS):
    delay = i * ANIM_DELAY_PER_ROW
    lines.append(
        f'.r{i}{{animation:reveal .001s {delay:.3f}s forwards;opacity:0;}}'
    )

lines.append("@keyframes reveal{to{opacity:1;}}")
lines.append("</style>")

for i, row in enumerate(ascii_rows):

    y = PAD_Y + i * CHAR_H

    row = (
        row.replace("&", "&amp;")
           .replace("<", "&lt;")
           .replace(">", "&gt;")
           .replace('"', "&quot;")
    )

    lines.append(
        f'<text class="r{i}" x="{PAD_X}" y="{y}">{row}</text>'
    )

lines.append("</svg>")

with open("ruru-ascii.svg", "w") as f:
    f.write("\n".join(lines))

print(f"Generated {ROWS} rows")
print(f"SVG size : {SVG_W} x {SVG_H}")
