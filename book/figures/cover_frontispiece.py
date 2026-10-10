#!/usr/bin/env python3
"""Frontispiece: a periodic array of quantized vortices of alternating sign in a 2D superfluid, computed with the qf-pgpe engine of rusty-SUNDIALS
(imprint_v2 + 15 time units of projected-GPE evolution). Phase as colour, density as brightness."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, "/mnt/data/xdev-cache/qf_ext")
from figstyle import *
import qf_pgpe
from matplotlib.colors import LightSource
N, L = 256, 64.0
s = qf_pgpe.Pgpe(N, L)
pos, q = [], []
for i in range(4):
    for j in range(4):
        pos.append([(i + 0.5) * L / 4 + 0.9 * np.sin(1.7 * j + i), (j + 0.5) * L / 4 + 0.9 * np.cos(2.3 * i + j)]); q.append(1 if (i + j) % 2 == 0 else -1)
c = s.imprint_v2(s.uniform(), np.array(pos), np.array(q))
c = s.run(c, 15.0)
psi = np.fft.ifft2(np.asarray(c))
n = np.abs(psi) ** 2; ph = np.angle(psi)
fig = plt.figure(figsize=(6.2, 6.2), facecolor="#101820"); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
rgb = vortex_cmap()((ph + np.pi) / (2 * np.pi))[..., :3]
b = np.clip(n / np.percentile(n, 99), 0, 1) ** 0.7
img = rgb * (0.12 + 0.88 * b[..., None])
ax.imshow(np.transpose(img, (1, 0, 2)), origin="lower", extent=[0, L, 0, L], interpolation="bilinear")
fig.savefig(FIG / "cover_frontispiece.pdf", dpi=300); fig.savefig(FIG / "cover_frontispiece.png", dpi=160); print("ok", float(n.min()), float(n.max()), len(pos))
