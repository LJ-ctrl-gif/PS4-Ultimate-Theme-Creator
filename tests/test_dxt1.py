import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from app.dxt1 import encode_dds, decode_dds, compress_dxt1a
from app.config import (dds_bytes_for, ANIMATED_FRAME_BYTES, MAX_FRAMES,
                        MAX_FRAME_COUNT, RAF_SIZE_LIMIT)

# 1. Header / size correctness
img = np.zeros((720, 1280, 4), np.uint8); img[..., 3] = 255
dds = encode_dds(img)
print("header magic      :", dds[:4])
print("size 1280x720     :", len(dds), "expected", dds_bytes_for(1280, 720), "match:", len(dds) == ANIMATED_FRAME_BYTES)
import struct
h, w = struct.unpack_from("<II", dds, 12)
print("header h,w        :", h, w)
print("fourcc            :", dds[84:88])
print("hdr size field    :", struct.unpack_from("<I", dds, 4)[0], "(must be 124)")
print("mipmapcount       :", struct.unpack_from("<I", dds, 28)[0], "(must be 0)")
print("linearsize        :", struct.unpack_from("<I", dds, 20)[0], "expected", len(dds)-128)
print("MAX_FRAMES        :", MAX_FRAMES, "-> total", MAX_FRAMES*ANIMATED_FRAME_BYTES,
      "bytes de", RAF_SIZE_LIMIT, f"(y tope de {MAX_FRAME_COUNT} frames)")
print()

# 2. Quality: gradient + noise + photo-ish content
rng = np.random.default_rng(0)
yy, xx = np.mgrid[0:720, 0:1280].astype(np.float32)
test = np.zeros((720, 1280, 4), np.uint8)
test[..., 0] = (xx / 1280 * 255)
test[..., 1] = (yy / 720 * 255)
test[..., 2] = (np.sin(xx / 40) * 127 + 128)
test[..., 3] = 255
t0 = time.time()
dds = encode_dds(test)
enc_ms = (time.time() - t0) * 1000
back = decode_dds(dds)
err = np.abs(back[..., :3].astype(np.int16) - test[..., :3].astype(np.int16))
mse = (err.astype(np.float64) ** 2).mean()
psnr = 10 * np.log10(255**2 / mse) if mse > 0 else 999
print(f"gradient  encode  : {enc_ms:.0f} ms   PSNR {psnr:.2f} dB   maxerr {err.max()}  meanerr {err.mean():.2f}")

# 3. Flat colour block must be exact-ish and use a valid mode
flat = np.zeros((64, 64, 4), np.uint8); flat[..., :3] = [200, 50, 90]; flat[..., 3] = 255
b = decode_dds(encode_dds(flat))
print("flat colour       : decoded", b[0, 0], "expected ~[200 50 90] (565 rounding)", "alpha", b[0,0,3])

# 4. Punchthrough: transparent pixels must decode with alpha 0, opaque stay opaque
pt = np.zeros((16, 16, 4), np.uint8)
pt[..., :3] = [255, 0, 0]
pt[..., 3] = 255
pt[0:8, 0:8, 3] = 0
d = decode_dds(encode_dds(pt))
print("punchthrough      : clear-region alpha", d[0:8,0:8,3].max(), "(must be 0)   opaque-region alpha", d[8:,8:,3].min(), "(must be 255)")
print("                    opaque colour preserved:", d[8, 8, :3])

# 5. Verify mode bit: opaque image must produce colour0 > colour1 blocks
raw = compress_dxt1a(test)
blocks = np.frombuffer(raw, np.uint8).reshape(-1, 8)
p0 = blocks[:,0].astype(np.uint32) | (blocks[:,1].astype(np.uint32) << 8)
p1 = blocks[:,2].astype(np.uint32) | (blocks[:,3].astype(np.uint32) << 8)
print(f"opaque blocks in 4-colour mode: {(p0>p1).mean()*100:.2f}%  (rest are flat blocks where p0==p1: {(p0==p1).mean()*100:.2f}%)")
print("  any p0<p1 in fully-opaque image (would be a bug):", bool((p0<p1).any()))

# 6. Non-multiple-of-4 dimensions
odd = np.zeros((127, 129, 4), np.uint8); odd[..., 3] = 255; odd[..., 0] = 128
o = encode_dds(odd)
print("odd dims 129x127  :", len(o), "expected", dds_bytes_for(129,127), "decode shape", decode_dds(o).shape)
