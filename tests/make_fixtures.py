"""Genera los archivos de prueba con ffmpeg.

Los tests esperan sample.mp4 / sample.gif / sample.png en esta misma carpeta.
Se generan en vez de guardarlos en el repo: son deterministas y pesan poco
cuando hacen falta.

    python tests\\make_fixtures.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: Duracion rara a proposito: obliga a que el fps de extraccion se calcule
#: bien en vez de asumir un valor redondo.
FIXTURES = [
    ("sample.mp4", ["-f", "lavfi", "-i", "testsrc2=size=854x480:rate=30:duration=7.3",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p"]),
    ("sample.gif", ["-f", "lavfi", "-i", "smptebars=size=640x360:rate=12:duration=3",
                    "-vf", "scale=320:180"]),
    # 4:3 a proposito: asi se comprueba que el recorte a 16:9 no deforma.
    ("sample.png", ["-f", "lavfi", "-i", "testsrc2=size=800x600", "-frames:v", "1"]),
    # Audio para los efectos: corto y a 44.1 kHz, para que haya que reconvertir.
    ("sample_sfx.wav", ["-f", "lavfi", "-i", "sine=frequency=880:duration=0.4",
                        "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le"]),
    # Musica: dos tonos distintos por canal, asi se comprueba que el estereo
    # sobrevive a la conversion a ATRAC9.
    ("sample_music.mp3", ["-f", "lavfi", "-i", "sine=frequency=330:duration=6",
                          "-f", "lavfi", "-i", "sine=frequency=440:duration=6",
                          "-filter_complex", "[0][1]amerge=inputs=2",
                          "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame"]),
    # Senuelo: un wav con extension .at9, para probar la validacion.
    ("notaudio.at9", ["-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                      "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", "-f", "wav"]),
]


def make_at9() -> None:
    """sample.at9: un .at9 de verdad para probar la subida sin conversion.

    Antes este archivo estaba guardado en el repo, pero era el bgm_home.at9
    sacado de un tema comercial. Se genera con el mismo encoder que usa la app,
    asi que ademas sirve de comprobacion de que produce lo que toca.
    """
    sys.path.insert(0, str(HERE.parent))
    from app import at9

    dest = HERE / "sample.at9"
    if not at9.available():
        print("  sample.at9     omitido: hace falta at9tool.exe (ver README)")
        if dest.exists():
            dest.unlink()
        return

    wav = HERE / "_at9_src.wav"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "lavfi", "-i", "sine=frequency=330:duration=8",
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(wav)],
        check=True,
    )
    try:
        at9.encode(wav, dest)
        print(f"  {'sample.at9':14} {dest.stat().st_size:>9,} B")
    finally:
        wav.unlink(missing_ok=True)


def main() -> int:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("Falta ffmpeg en el PATH.")
        return 1

    for name, args in FIXTURES:
        dest = HERE / name
        proc = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *args, str(dest)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not dest.exists():
            print(f"FALLO {name}: {proc.stderr.strip()[:200]}")
            return 1
        print(f"  {name:14} {dest.stat().st_size:>9,} B")

    make_at9()

    print("\nListo. Ahora levanta el servidor en el 8000 y corre los tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
