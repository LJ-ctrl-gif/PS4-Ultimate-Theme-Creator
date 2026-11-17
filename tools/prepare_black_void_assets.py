#!/usr/bin/env python3
"""Download BLACK VOID artwork and generate PS4-sized glow icon variants.

Usage:
    python -m pip install Pillow
    python tools/prepare_black_void_assets.py

Outputs are written to BLACK_VOID_ASSETS/ for manual import into the theme
builder. This script does not create a PKG or include Sony packaging tools.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from PIL import Image, ImageFilter, ImageChops

ROOT = Path("BLACK_VOID_ASSETS")
BACKGROUNDS = {
    "homescreen.png": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:02f71d3a-777f-4641-91f1-d6ae11e2cc6a",
    "functionscreen.png": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:b5779301-d818-42c8-959b-8be4e83d4736",
}
FUNCTION = {
    "community": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:3e15042d-ebdf-40cc-8f9e-7c71297afcda",
    "event": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:2dfa9bc6-a9b6-435e-b428-b74bfec4854a",
    "friend": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:c26ca465-d5b0-475a-bfe5-c2a2d96d3234",
    "message": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:81430e5f-d0ea-4266-be94-aa0b7fece25b",
    "notification": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:96095470-526c-44b4-ae27-8c898ae33018",
    "party": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:b5f76dd4-7bb5-4b9a-b005-326503696fc0",
    "power": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:a8b1abd1-b935-420c-87ac-a6f89cbdc825",
    "setting": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:956e08b1-5fbd-4ebd-a1bf-6dbc5c4e3b2a",
    "trophy": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:1c50f2b4-7339-4d11-b850-222e3b9d63ea",
}
CONTENT = {
    "browser": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:dc1c5d5a-75d3-4707-9c5e-4a3edcd0810d",
    "disc": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5e8bd3f9-54e0-4156-8d3e-c25c18d23368",
    "discoverlay": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5639f83f-f743-4d3e-a7da-7806b5c57748",
    "folder": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:82c0b9e3-5e4a-4005-851b-af925c06d4b1",
    "gallery": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:c199133a-aa1e-4124-9ba3-413dfa30d4da",
    "library": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:0aec1794-48d6-4eff-8b3b-9110fcaa33a7",
    "livefromps": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:6074ea6c-68a8-43e2-9bf8-7e986bc9c96f",
    "shareplay": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:d7ffa59d-0863-4905-a44b-dabb59934629",
    "tvvideo": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:363cb601-b4b9-46e6-85c7-b53d484e4f5a",
    "usbmusic": "https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:acbdb8a5-9c2e-4434-a17c-e2f7dc9b4875",
}

def download(url: str) -> Image.Image:
    request = Request(url, headers={"User-Agent": "BLACK-VOID-asset-preparer/1.0"})
    with urlopen(request, timeout=45) as response:
        data = response.read()
    image = Image.open(BytesIO(data))
    image.load()
    return image.convert("RGBA")

def fit_contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(image, ((size[0] - image.width)//2, (size[1] - image.height)//2))
    return canvas

def make_glow(source: Image.Image) -> Image.Image:
    # Preserve the silver icon while adding a restrained cool-silver outer halo.
    icon = fit_contain(source, (128, 128))
    alpha = icon.getchannel("A")
    expanded = Image.new("L", (152, 152), 0)
    expanded.paste(alpha, (12, 12))
    halo = expanded.filter(ImageFilter.GaussianBlur(5))
    halo = halo.point(lambda value: min(150, int(value * 0.9)))
    glow = Image.new("RGBA", (152, 152), (190, 205, 220, 0))
    glow.putalpha(halo)
    base = Image.new("RGBA", (152, 152), (0, 0, 0, 0))
    base.alpha_composite(glow)
    base.alpha_composite(fit_contain(source, (128, 128)), (12, 12))
    return base

def save_image(image: Image.Image, path: Path, size: tuple[int, int] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    image.save(path, "PNG", optimize=True)

def main() -> None:
    bg_dir = ROOT / "backgrounds"
    fn_dir = ROOT / "function_icons"
    ct_dir = ROOT / "content_icons"
    for filename, url in BACKGROUNDS.items():
        save_image(download(url), bg_dir / filename, (1920, 1080))
        print(f"OK background: {filename}")
    for name, url in FUNCTION.items():
        source = download(url)
        save_image(fit_contain(source, (128, 128)), fn_dir / f"{name}.png")
        save_image(make_glow(source), fn_dir / f"{name}_glow.png")
        print(f"OK function icon + glow: {name}")
    for name, url in CONTENT.items():
        save_image(fit_contain(download(url), (512, 512)), ct_dir / f"{name}.png")
        print(f"OK content icon: {name}")
    print(f"\nPrepared 30 PNG files in: {ROOT.resolve()}")
    print("Import them into the builder's matching background, function-icon, and content-icon slots.")
    print("This is an artwork preparation step only; it does not build or validate a PS4 PKG.")

if __name__ == "__main__":
    main()
