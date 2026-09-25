"""Build a transparent, looping GIF of Moby's thinking → solving animation.

Uses the keyed frames in build/moby (run scripts/prep.sh first).
  python3 scripts/make_gif.py            → out/moby-thinking-solving.gif
"""
import glob
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out', 'moby-thinking-solving.gif')
HEIGHT = 640          # output height in px
STEP = 1              # 1 = every source frame (~24fps), 2 = ~12fps
COLOURS = 127         # + 1 transparent slot
HOLD_MS = 1000        # pause on the solved pose before looping

paths = sorted(glob.glob(os.path.join(ROOT, 'build', 'moby', '*.png')))[::STEP]
frames = [Image.open(p).convert('RGBA') for p in paths]
box = frames[0].getbbox()
for f in frames[1:]:
    b = f.getbbox()
    box = (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
box = (max(box[0] - 4, 0), max(box[1] - 4, 0), box[2] + 4, box[3] + 4)
w = round((box[2] - box[0]) * HEIGHT / (box[3] - box[1]))
frames = [f.crop(box).resize((w, HEIGHT), Image.LANCZOS) for f in frames]

# One palette for every frame, built from a sample across the whole clip.
sample = Image.new('RGB', (w, HEIGHT * 6))
for k, f in enumerate(frames[:: max(1, len(frames) // 6)][:6]):
    sample.paste(f.convert('RGB'), (0, HEIGHT * k))
pal_img = sample.quantize(COLOURS, method=Image.MEDIANCUT, dither=Image.NONE)
palette = pal_img.getpalette()[: COLOURS * 3]
palette += [0, 0, 0] * (256 - COLOURS)          # slot COLOURS = transparent
pal_img.putpalette(palette)

out = []
for f in frames:
    rgb = f.convert('RGB').quantize(palette=pal_img, dither=Image.NONE)
    idx = np.asarray(rgb).copy()
    idx[np.asarray(f)[..., 3] < 128] = COLOURS
    q = Image.fromarray(idx.astype(np.uint8), 'P')
    q.putpalette(palette)
    out.append(q)

fps = 24.1 / STEP
durations = [round(1000 / fps)] * len(out)
durations[-1] = HOLD_MS
out[0].save(OUT, save_all=True, append_images=out[1:], duration=durations, loop=0,
            transparency=COLOURS, disposal=2, optimize=False)
print(f'{OUT}: {len(out)} frames, {w}x{HEIGHT}, {os.path.getsize(OUT) / 1e6:.1f} MB')
