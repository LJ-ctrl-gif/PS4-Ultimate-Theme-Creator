#!/usr/bin/env python3
"""Assemble BLACK VOID artwork into the canonical PS4 theme image layout."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "BLACK_VOID_ASSETS"
OUT = ROOT / "dist" / "BLACK-VOID-theme-assets.zip"

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    required = []
    with ZipFile(OUT, "w", ZIP_DEFLATED, compresslevel=9) as z:
        def add(source, target):
            p = SRC / source
            if not p.is_file():
                raise SystemExit(f"Missing preset asset: {p}")
            z.write(p, target)
            required.append(target)

        add("backgrounds/homescreen.png", "Image0/texture/background/homescreen.png")
        add("backgrounds/functionscreen.png", "Image0/texture/background/functionscreen.png")
        for name in ("community","event","friend","message","notification","party","power","setting","trophy"):
            add(f"function_icons/{name}.png", f"Image0/texture/function_icon/{name}.png")
            add(f"function_icons/{name}_glow.png", f"Image0/texture/function_icon/{name}_glow.png")
        for name in ("browser","disc","discoverlay","folder","gallery","library","livefromps","shareplay","tvvideo","usbmusic"):
            add(f"content_icons/{name}.png", f"Image0/texture/content_icon/{name}.png")

        with Image.open(SRC / "backgrounds/homescreen.png") as im:
            im.convert("RGBA").resize((740,416), Image.Resampling.LANCZOS).save(ROOT / "dist" / "preview.png")
            im.convert("RGBA").resize((512,512), Image.Resampling.LANCZOS).save(ROOT / "dist" / "icon0.png")
        z.write(ROOT / "dist" / "preview.png", "Image0/texture/preview.png")
        z.write(ROOT / "dist" / "icon0.png", "Sc0/sce_sys/icon0.png")
        z.writestr("README.txt", "BLACK VOID PS4 theme artwork preset. Image assets only; not an installable PKG. Import the images into PS4 Ultimate Theme Creator, complete theme metadata, then package using legally obtained compatible tools.\n\nMANIFEST.sha256 lists the SHA-256 digest of every PNG in this archive. Verify it before importing if you suspect corruption.")
    manifest = []
    with ZipFile(OUT, "r") as archive:
        for name in sorted(n for n in archive.namelist() if n.lower().endswith(".png")):
            manifest.append(f"{sha256(archive.read(name)).hexdigest()}  {name}")
    with ZipFile(OUT, "a", ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("MANIFEST.sha256", "\n".join(manifest) + "\n")
    print(f"Created {OUT} with {len(required)+2} mapped PNG files.")

if __name__ == "__main__":
    main()
