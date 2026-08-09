"""Backends de codificacion a .dds.

Hay dos caminos y los dos producen DXT1a sin mipmaps:

* `native`  -- el encoder de [dxt1.py]. No depende de nada instalado.
* `magick`  -- ImageMagick, solo si el binario `magick` esta en el PATH.

Sobre el comando clasico de los tutoriales de temas
(`convert img.png -define dds:compression=dxt1a ...`): en Windows `convert`
es el conversor FAT->NTFS que trae el sistema en system32, no ImageMagick.
Por eso este modulo solo busca `magick`, que no choca con nada.
"""

from __future__ import annotations

import os
import subprocess
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, Iterator

import numpy as np

from .dxt1 import encode_dds
from .media import MAGICK, NO_WINDOW, MediaError, flatten_alpha

NATIVE = "native"
MAGICK_BACKEND = "magick"
DEFAULT_BACKEND = NATIVE

#: numpy releases the GIL on the heavy operations, so threading the
#: compression really does help (~2.7x measured with 4 threads).
ENCODE_WORKERS = min(4, (os.cpu_count() or 2))


def available_backends() -> list[str]:
    backends = [NATIVE]
    if MAGICK:
        backends.append(MAGICK_BACKEND)
    return backends


def _encode_with_magick(rgba: np.ndarray) -> bytes:
    """Manda el frame crudo a ImageMagick por stdin y recibe el .dds por stdout.

    `-alpha off` va antes de las opciones dds a proposito: si la imagen llega
    con canal alpha, ImageMagick elige DXT5 por su cuenta, que pesa el doble
    por pixel y tira el limite de 16MB.
    """
    height, width = rgba.shape[:2]
    cmd = [
        MAGICK,
        "-size", f"{width}x{height}", "-depth", "8", "rgba:-",
        "-alpha", "off",
        "-define", "dds:compression=dxt1a",
        "-define", "dds:mipmaps=0",
        "dds:-",
    ]
    proc = subprocess.run(
        cmd,
        input=rgba.tobytes(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=NO_WINDOW,
    )
    if proc.returncode != 0 or not proc.stdout:
        tail = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        raise MediaError("ImageMagick failed: " + ("\n".join(tail[-4:]) or "no output"))

    data = proc.stdout
    if data[84:88] != b"DXT1":
        raise MediaError(
            f"ImageMagick escribio {data[84:88]!r} en vez de DXT1. "
            "Esa version no entiende 'dxt1a'; usa el encoder nativo."
        )
    return data


def encode_frame(rgba: np.ndarray, backend: str = DEFAULT_BACKEND) -> bytes:
    """RGBA -> archivo .dds completo (DXT1a, sin mipmaps)."""
    opaque = flatten_alpha(rgba)
    if backend == MAGICK_BACKEND:
        if not MAGICK:
            raise MediaError("ImageMagick is not installed (no `magick` on PATH).")
        return _encode_with_magick(opaque)
    if backend != NATIVE:
        raise MediaError(f"Unknown backend: {backend}")
    return encode_dds(opaque)


def encode_sequence(
    frames: Iterable[np.ndarray], backend: str = DEFAULT_BACKEND
) -> Iterator[tuple[int, bytes]]:
    """Comprime una secuencia de frames y los devuelve en orden.

    Comprime en paralelo mientras ffmpeg sigue decodificando, pero solo deja
    unos pocos frames en vuelo: a 3.5MB cada uno, encolarlos todos se comeria
    mas de 100MB sin ganar nada.
    """
    in_flight = ENCODE_WORKERS * 2
    with ThreadPoolExecutor(max_workers=ENCODE_WORKERS) as pool:
        pending: deque = deque()
        for index, rgba in enumerate(frames):
            pending.append((index, pool.submit(encode_frame, rgba, backend)))
            if len(pending) >= in_flight:
                done_index, future = pending.popleft()
                yield done_index, future.result()
        while pending:
            done_index, future = pending.popleft()
            yield done_index, future.result()
