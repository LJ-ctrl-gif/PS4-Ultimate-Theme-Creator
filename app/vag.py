"""Codificador VAG (PS-ADPCM), el formato de los efectos de sonido del tema.

A diferencia de ATRAC9, este si se puede generar: PS-ADPCM esta documentado y
es sencillo. Cada bloque de 16 bytes guarda 28 muestras comprimidas a 4 bits,
con un predictor y un desplazamiento elegidos por bloque.

    byte 0    (predictor << 4) | shift
    byte 1    flags (fin de audio, bucle...)
    bytes 2..15   28 nibbles, primero el bajo

El archivo empieza con una cabecera "VAGp" de 48 bytes en big-endian y un
bloque de silencio, que es lo que espera el decodificador.

Verificacion: lo que sale de aqui lo vuelve a leer ffmpeg (que trae su propio
decodificador `adpcm_psx`, independiente de este codigo) y la onda coincide.
"""

from __future__ import annotations

import struct

import numpy as np

MAGIC = b"VAGp"
VERSION = 0x20
HEADER_SIZE = 48
SAMPLES_PER_BLOCK = 28
BLOCK_SIZE = 16

#: The predictor's 5 filters, in 1/64 units.
FILTERS = np.array(
    [[0, 0], [60, 0], [115, -52], [98, -55], [122, -60]], dtype=np.float64
) / 64.0

#: End marker on the last block: stop and mute.
FLAG_END = 0x01
FLAG_NONE = 0x00


def _encode_block(samples: np.ndarray, hist: list[float]) -> tuple[bytes, list[float]]:
    """Comprime 28 muestras probando cada predictor y quedandose con el mejor.

    `hist` son las dos muestras ya decodificadas anteriores; hay que llevarlas
    porque el predictor las usa, y tienen que ser las que vera el
    decodificador, no las originales.
    """
    best = None
    for predictor, (c0, c1) in enumerate(FILTERS):
        h0, h1 = hist
        # Residual against what the filter predicts.
        residuals = np.empty(len(samples))
        p0, p1 = h0, h1
        for i, s in enumerate(samples):
            residuals[i] = s - (p0 * c0 + p1 * c1)
            p1, p0 = p0, s

        # The decoder scales the nibble as (n << 12) >> shift, i.e. multiplying
        # by 2^(12-shift): more shift, more resolution. Pick the largest shift
        # (finest step) where the residual still fits in a signed 4-bit value.
        peak = np.abs(residuals).max()
        shift = 12
        while shift > 0 and 7.0 * (1 << (12 - shift)) < peak:
            shift -= 1
        scale = 1 << (12 - shift)

        # Simulate decoding to measure the real error.
        nibbles = np.empty(len(samples), dtype=np.int32)
        d0, d1 = h0, h1
        error = 0.0
        for i, s in enumerate(samples):
            predicted = d0 * c0 + d1 * c1
            q = int(np.clip(round((s - predicted) / scale), -8, 7))
            nibbles[i] = q
            decoded = predicted + q * scale
            decoded = float(np.clip(decoded, -32768, 32767))
            error += (s - decoded) ** 2
            d1, d0 = d0, decoded

        if best is None or error < best[0]:
            best = (error, predictor, shift, nibbles, [d0, d1])

    _err, predictor, shift, nibbles, new_hist = best
    out = bytearray(BLOCK_SIZE)
    out[0] = (predictor << 4) | shift
    out[1] = FLAG_NONE
    for i in range(0, SAMPLES_PER_BLOCK, 2):
        low = int(nibbles[i]) & 0x0F
        high = int(nibbles[i + 1]) & 0x0F
        out[2 + i // 2] = (high << 4) | low
    return bytes(out), new_hist


def encode(pcm: np.ndarray, sample_rate: int, name: str = "se") -> bytes:
    """PCM mono de 16 bits -> archivo .vag completo.

    `pcm` es un array de enteros con signo; se rellena hasta un multiplo de 28
    muestras porque los bloques son de tamano fijo.
    """
    if pcm.ndim != 1:
        raise ValueError("VAG is mono: pass a single channel")

    samples = pcm.astype(np.float64)
    remainder = len(samples) % SAMPLES_PER_BLOCK
    if remainder:
        samples = np.pad(samples, (0, SAMPLES_PER_BLOCK - remainder))

    blocks = bytearray()
    # Leading silence block: what Sony's own tool writes and what decoders
    # expect to find.
    blocks += bytes(BLOCK_SIZE)

    hist = [0.0, 0.0]
    for start in range(0, len(samples), SAMPLES_PER_BLOCK):
        block, hist = _encode_block(samples[start:start + SAMPLES_PER_BLOCK], hist)
        blocks += block

    # The last block flags the end.
    if len(blocks) > BLOCK_SIZE:
        blocks[-BLOCK_SIZE + 1] = FLAG_END

    header = (
        MAGIC
        + struct.pack(">I", VERSION)
        + struct.pack(">I", 0)
        + struct.pack(">I", len(blocks))
        + struct.pack(">I", sample_rate)
        + bytes(12)
        + name.encode("ascii", "replace")[:16].ljust(16, b"\x00")
    )
    assert len(header) == HEADER_SIZE, len(header)
    return header + bytes(blocks)


def decode(data: bytes) -> tuple[np.ndarray, int]:
    """Decodifica un .vag. Se usa para comprobar el codificador."""
    if data[:4] != MAGIC:
        raise ValueError("not a VAG")
    sample_rate = struct.unpack_from(">I", data, 0x10)[0]

    out: list[float] = []
    h0 = h1 = 0.0
    for off in range(HEADER_SIZE, len(data) - BLOCK_SIZE + 1, BLOCK_SIZE):
        block = data[off:off + BLOCK_SIZE]
        shift = block[0] & 0x0F
        predictor = min(block[0] >> 4, len(FILTERS) - 1)
        if block[1] & 0x07 == 0x07:      # fin
            break
        c0, c1 = FILTERS[predictor]
        for i in range(SAMPLES_PER_BLOCK):
            byte = block[2 + i // 2]
            nibble = (byte & 0x0F) if i % 2 == 0 else (byte >> 4)
            if nibble > 7:
                nibble -= 16
            value = nibble * (1 << (12 - shift)) + h0 * c0 + h1 * c1
            value = float(np.clip(value, -32768, 32767))
            out.append(value)
            h1, h0 = h0, value

    return np.array(out, dtype=np.int16), sample_rate
