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

def refine(avg, sigma=2.0, contrast=0.0, post_sigma=0.8):
    """avg: grayscale average in [0,1]. contrast: px of x-growth / y-shrink."""
    out = ndimage.gaussian_filter(avg.astype(np.float32), sigma) if sigma else avg.astype(np.float32)
    if contrast:
        t = int(round(contrast))
        if t > 0:
            out = ndimage.grey_dilation(out, size=(1, 2*t+1))
            out = ndimage.grey_erosion(out, size=(2*t+1, 1))
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
