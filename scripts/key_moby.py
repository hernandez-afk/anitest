"""Knock the near-white backdrop out of the Moby clip frames.

The backdrop is flood-filled from the frame border, so the white eyes and
controller (enclosed by Moby's dark outline) stay opaque.
Reads build/moby_raw/*.png, writes build/moby/*.png (RGBA).
"""
import glob
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'build', 'moby_raw')
DST = os.path.join(ROOT, 'build', 'moby')
os.makedirs(DST, exist_ok=True)

for p in sorted(glob.glob(SRC + '/*.png')):
    im = Image.open(p).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    light = (a.min(2) > 200) & ((a.max(2) - a.min(2)) < 30)
    lab, _ = ndimage.label(light)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    # Pull the matte 2px inside the anti-aliased rim so no light fringe survives,
    # and paint everything outside it in Moby's outline colour so the soft edge
    # blends into the outline instead of into white.
    bg = ndimage.binary_dilation(bg, iterations=2)
    ring = ndimage.binary_dilation(bg, iterations=3) & ~bg
    outline = np.median(a[ring], axis=0).astype(np.uint8) if ring.any() else np.array([0, 73, 95], np.uint8)
    rgb = np.asarray(im).copy()
    rgb[bg] = outline
    alpha = Image.fromarray((~bg).astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.fromarray(rgb).convert('RGBA')
    out.putalpha(alpha)
    out.save(os.path.join(DST, os.path.basename(p)))

print('keyed', len(os.listdir(DST)), 'frames')
