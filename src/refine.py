"""Smooth the averaged templates and increase stroke contrast.

Layton's type is a broad-nib design: vertical strokes thick, horizontals thin.
Widening that difference means growing the shape along x (which thickens vertical
stems but only lengthens horizontal bars) and shrinking it along y (which thins
horizontal bars but only shortens vertical stems). Diagonals see both and stay put.
The ink bbox is restored afterwards, so proportions and placement are unchanged and
only the thick/thin ratio moves.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

def _bbox(b):
    ys, xs = np.where(b)
    return ys.min(), ys.max()+1, xs.min(), xs.max()+1

def _disk(r):
    y, x = np.ogrid[-r:r+1, -r:r+1]
    return (x*x + y*y) <= r*r + 0.1

def refine(avg, sigma=2.0, contrast=0.0, weight=0.0, lighten=0.0, post_sigma=0.8):
    """avg: grayscale average in [0,1]. contrast: px of x-growth / y-shrink.
    weight: px of uniform growth (+) or shrink (-) of every stroke; the ink box is
    restored afterwards, so a negative weight is a lighter cut at the same letter height.
    lighten: fraction of its own width that every stroke loses. Unlike `weight`, this
    keeps the thick/thin ratio exactly, so the result is the same design at a lighter
    weight rather than a higher-contrast one."""
    out = ndimage.gaussian_filter(avg.astype(np.float32), sigma) if sigma else avg.astype(np.float32)
    if contrast:
        t = int(round(contrast))
        if t > 0:
            out = ndimage.grey_dilation(out, size=(1, 2*t+1))
            out = ndimage.grey_erosion(out, size=(2*t+1, 1))
    if weight:
        w = int(round(abs(weight)))
        out = (ndimage.grey_dilation if weight > 0 else ndimage.grey_erosion)(out, footprint=_disk(w))
    if lighten:
        ink = out > 0.5
        d = ndimage.distance_transform_edt(ink)                 # distance to background
        # local half stroke width: the ridge value nearest each pixel (separable max window)
        W = ndimage.grey_dilation(d, size=(61, 61))
        keep = d > lighten * W
        # rebuild a soft edge for the tracer: distance inside the new shape, clipped to 1px
        dn = ndimage.distance_transform_edt(keep) - ndimage.distance_transform_edt(~keep)
        out = np.clip(0.5 + 0.5*dn, 0, 1).astype(np.float32)
    if post_sigma:
        out = ndimage.gaussian_filter(out, post_sigma)
    # restore the original ink box so proportions and baseline placement do not drift
    o = _bbox(avg > 0.5)
    m = out > 0.5
    if not m.any(): return out
    n = _bbox(m)
    crop = out[n[0]:n[1], n[2]:n[3]]
    h, w = o[1]-o[0], o[3]-o[2]
    res = np.asarray(Image.fromarray((np.clip(crop,0,1)*255).astype(np.uint8))
                     .resize((max(w,1), max(h,1)), Image.LANCZOS)).astype(np.float32)/255.0
    fixed = np.zeros_like(out)
    fixed[o[0]:o[1], o[2]:o[3]] = res
    return fixed
