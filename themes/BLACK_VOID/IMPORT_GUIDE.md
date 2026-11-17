# BLACK VOID artwork import

The artwork preparation script is at `tools/prepare_black_void_assets.py`.

## Prepare the PNG files

Run from the repository root:

```bash
python -m pip install Pillow
python tools/prepare_black_void_assets.py
```

The script downloads the two 1920x1080 backgrounds, nine 128x128 function icons,
creates nine 152x152 silver-halo glow variants, and downloads ten 512x512
content icons. It writes 30 PNG files into `BLACK_VOID_ASSETS/`.

## Import mapping

- `backgrounds/homescreen.png` → Home background
- `backgrounds/functionscreen.png` → Top menu background
- `function_icons/<name>.png` → matching function icon
- `function_icons/<name>_glow.png` → matching function icon glow
- `content_icons/<name>.png` → matching content icon

Keep the filenames unchanged. Check the builder preview for clipping and
contrast before packaging.

## Package status

This guide and script prepare artwork only. They do not create a PS4 PKG.
The builder still requires its documented Windows packaging environment and
the proprietary packaging binaries that are not included in this repository.
A generated package must be validated before anyone calls it installable.
