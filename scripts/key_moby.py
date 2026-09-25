"""Knock the near-white backdrop out of the Moby clip frames.

The backdrop is flood-filled from the frame border, so the white eyes and
controller (enclosed by Moby's dark outline) stay opaque.
Reads build/moby_raw/*.png, writes build/moby/*.png (RGBA), padded by PAD px
top and bottom. In a few source frames Moby's squash-and-stretch runs past the
edge of the video, which slices off his outline; those edges are closed with a
curved cap that continues the body's own curvature.
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
PAD = 24


def outer_span(alpha_row):
    xs = np.where(alpha_row > 128)[0]
    return (xs.min(), xs.max()) if len(xs) else None


def cap(img, edge_y, step, colour):
    """Close the contour past row edge_y (moving by `step`: -1 up, +1 down).

    Each side of the cut outline is continued along its own tangent (measured
    over the last few rows), and the two sides are joined with an elliptical
    cap, so a tilted outline stays tilted instead of turning into a flat dome.
    """
    a = img[..., 3]
    s0 = outer_span(a[edge_y])
    s4 = outer_span(a[edge_y - step * 4])
    if s0 is None or s4 is None:
        return
    xl0, xr0 = s0
    sl = (xl0 - s4[0]) / 4          # outward drift of each side per row
    sr = (xr0 - s4[1]) / 4
    w = xr0 - xl0
    closing = sr - sl               # how fast the gap closes per row (negative = closing)
    height = w / -closing if closing < -0.2 else w * 0.12
    height = float(np.clip(height * 0.55, 2, PAD - 4))
    apex = (xl0 + sl * height + xr0 + sr * height) / 2
    apex = float(np.clip(apex, xl0, xr0))
    for k in range(1, int(np.ceil(height)) + 1):
        f = k / height
        if f >= 1:
            break
        shrink = 1 - np.sqrt(1 - f * f)                 # 0 at the cut → 1 at the apex
        x0 = xl0 + (apex - xl0) * shrink
        x1 = xr0 + (apex - xr0) * shrink
        y = edge_y + step * k
        img[y, int(round(x0)):int(round(x1)) + 1, :3] = colour
        img[y, int(round(x0)):int(round(x1)) + 1, 3] = 255


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
    H, W = bg.shape
    img = np.zeros((H + 2 * PAD, W, 4), np.uint8)
    img[..., :3] = outline
    img[PAD:PAD + H, :, :3] = rgb
    img[PAD:PAD + H, :, 3] = (~bg) * 255
    if img[PAD, :, 3].any():
        cap(img, PAD, -1, outline)
    if img[PAD + H - 1, :, 3].any():
        cap(img, PAD + H - 1, 1, outline)
    alpha = Image.fromarray(img[..., 3]).filter(ImageFilter.GaussianBlur(0.8))
    out = Image.fromarray(img[..., :3]).convert('RGBA')
    out.putalpha(alpha)
    out.save(os.path.join(DST, os.path.basename(p)))

print('keyed', len(os.listdir(DST)), 'frames')
