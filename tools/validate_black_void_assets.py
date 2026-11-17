#!/usr/bin/env python3
"""Validate the committed BLACK VOID artwork set before it is published."""

from pathlib import Path
from PIL import Image

ROOT = Path("BLACK_VOID_ASSETS")
EXPECTED = {
    "backgrounds/homescreen.png": (1920, 1080),
    "backgrounds/functionscreen.png": (1920, 1080),
}
FUNCTION = (
    "community", "event", "friend", "message", "notification",
    "party", "power", "setting", "trophy",
)
CONTENT = (
    "browser", "disc", "discoverlay", "folder", "gallery",
    "library", "livefromps", "shareplay", "tvvideo", "usbmusic",
)
for name in FUNCTION:
    EXPECTED[f"function_icons/{name}.png"] = (128, 128)
    EXPECTED[f"function_icons/{name}_glow.png"] = (152, 152)
for name in CONTENT:
    EXPECTED[f"content_icons/{name}.png"] = (512, 512)

def main() -> None:
    missing = [p for p in EXPECTED if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("Missing artwork files:\n" + "\n".join(missing))

    errors = []
    for relative, dimensions in EXPECTED.items():
        path = ROOT / relative
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.format != "PNG":
                    errors.append(f"{relative}: expected PNG, got {image.format}")
                if image.size != dimensions:
                    errors.append(f"{relative}: expected {dimensions}, got {image.size}")
        except Exception as exc:
            errors.append(f"{relative}: invalid image ({exc})")

    extras = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and p.relative_to(ROOT).as_posix() not in EXPECTED
    )
    if errors:
        raise SystemExit("Artwork validation failed:\n" + "\n".join(errors))
    print(f"PASS: {len(EXPECTED)} PNG files have valid headers and expected dimensions.")
    if extras:
        print("Additional files (not counted): " + ", ".join(extras))

if __name__ == "__main__":
    main()
