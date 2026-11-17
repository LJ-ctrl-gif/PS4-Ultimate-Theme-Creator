# BLACK VOID — PS4 theme asset map

Visual direction: **jet black (#000000)** with restrained brushed-silver iconography and silver edge lighting.

## Generated assets (committed)

All 30 PNG files are now committed under `BLACK_VOID_ASSETS/`:

| Builder slot | Source file | Required size |
|---|---|---:|
| Home background | `backgrounds/homescreen.png` | 1920×1080 |
| Top menu background | `backgrounds/functionscreen.png` | 1920×1080 |
| Function icons | `function_icons/<name>.png` | 128×128 |
| Function icon glow | `function_icons/<name>_glow.png` | 152×152 |
| Content icons | `content_icons/<name>.png` | 512×512 |

Function icon names: `community`, `event`, `friend`, `message`, `notification`, `party`, `power`, `setting`, `trophy`.

Content icon names: `browser`, `disc`, `discoverlay`, `folder`, `gallery`, `library`, `livefromps`, `shareplay`, `tvvideo`, `usbmusic`.

## Builder import mapping

- `BLACK_VOID_ASSETS/backgrounds/homescreen.png` → Home background
- `BLACK_VOID_ASSETS/backgrounds/functionscreen.png` → Top menu background
- `BLACK_VOID_ASSETS/function_icons/<name>.png` → matching function icon
- `BLACK_VOID_ASSETS/function_icons/<name>_glow.png` → matching function icon glow
- `BLACK_VOID_ASSETS/content_icons/<name>.png` → matching content icon

Keep filenames unchanged. Check the builder preview for clipping and contrast before packaging.

## Validation and package status

The artwork workflow validates the PNG dimensions and expected file count before upload. Artwork preparation is separate from PS4 package creation. The builder's documented packaging environment and legitimate packaging binaries are still required to create a PKG. Any resulting package must be validated and tested on compatible hardware before being called installable.
