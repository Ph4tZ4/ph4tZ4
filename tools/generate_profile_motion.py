"""Regenerate the README motion strip and its still fallback (requires Pillow)."""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = '#0b1219'
ACCENT = '#6ee7df'
FONT = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
assert FONT.is_file(), 'Set FONT to an installed TrueType font before regenerating.'
font = ImageFont.truetype(str(FONT), 23)
small = ImageFont.truetype(str(FONT), 16)
frames = []

for frame in range(48):
    image = Image.new('RGB', (1200, 100), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.line((32, 99, 1168, 99), fill='#263640')
    draw.text((32, 35), 'BUILD. EXPLORE. CREATE.', font=font, fill=ACCENT)
    draw.text((780, 40), 'WEB / AI / 3D / GAMES', font=small, fill='#adbec9')
    for index in range(25):
        phase = frame * math.tau / 48 - index * 0.45
        height = 6 + 20 * (1 + math.sin(phase)) / 2
        x = 430 + index * 10
        draw.rounded_rectangle((x, 50 - height, x + 3, 50 + height), radius=1,
                               fill=ACCENT if index % 3 else '#2b6975')
    draw.ellipse((1104, 25, 1154, 75), outline='#295864', width=2)
    angle = frame * math.tau / 48
    x, y = 1129 + 25 * math.cos(angle), 50 + 25 * math.sin(angle)
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=ACCENT)
    draw.line((1122, 50, 1127, 55, 1136, 44), fill=ACCENT, width=2)
    frames.append(image.quantize(colors=64))

output = ROOT / 'assets' / 'profile-motion.gif'
frames[0].save(output, save_all=True, append_images=frames[1:],
               duration=80, loop=0, optimize=True, disposal=2)
frames[0].convert('RGB').save(ROOT / 'assets' / 'profile-motion-still.png')

with Image.open(output) as result:
    assert result.n_frames == 48
    assert result.size == (1200, 100)
    assert result.info['loop'] == 0
    result.seek(0)
    first = result.convert('RGB').tobytes()
    result.seek(12)
    assert first != result.convert('RGB').tobytes(), 'Animation frames must differ.'
assert output.stat().st_size < 500_000, 'Keep the profile animation lightweight.'
print(f'Generated and checked {output.name}: {output.stat().st_size:,} bytes')
