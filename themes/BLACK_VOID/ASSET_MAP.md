# BLACK VOID — PS4 theme asset map

Visual direction: near-black graphite, brushed-silver metal, restrained cool highlights, crisp silhouettes, transparent PNG backgrounds. Keep every icon readable at its target size.

## Function icons

Each item maps to a fixed builder slot. Export a 128x128 PNG plus a matching 152x152 glow PNG.

| Builder slot | Required filename | Visual concept |
|---|---|---|
| `fn:community` | `community.png` | group of people / community |
| `fn:event` | `event.png` | calendar or event marker |
| `fn:friend` | `friend.png` | single user / friends |
| `fn:message` | `message.png` | message bubble |
| `fn:notification` | `notification.png` | notification bell |
| `fn:party` | `party.png` | headset / party chat |
| `fn:power` | `power.png` | power symbol |
| `fn:setting` | `setting.png` | gear / settings |
| `fn:trophy` | `trophy.png` | trophy |

Glow filenames are the same names with `_glow` before `.png`, for example `power_glow.png`.

## Content icons

Each item maps to a fixed builder slot and must be exported as a 512x512 PNG.

| Builder slot | Required filename | Visual concept |
|---|---|---|
| `ct:browser` | `browser.png` | web browser / globe |
| `ct:disc` | `disc.png` | optical game disc |
| `ct:discoverlay` | `discoverlay.png` | disc with overlay treatment |
| `ct:folder` | `folder.png` | game folder |
| `ct:gallery` | `gallery.png` | photo / capture gallery |
| `ct:library` | `library.png` | game library / stacked cases |
| `ct:livefromps` | `livefromps.png` | live broadcast / screen |
| `ct:shareplay` | `shareplay.png` | shared play / two controllers |
| `ct:tvvideo` | `tvvideo.png` | television / video |
| `ct:usbmusic` | `usbmusic.png` | USB device / music note |

## Integration checklist

- [ ] Inspect the Firefly atlas and identify each symbol before cropping.
- [ ] Export nine function icons at 128x128 and their glow variants at 152x152.
- [ ] Export ten content icons at 512x512.
- [ ] Preserve transparency and use consistent silver/graphite styling.
- [ ] Upload through the builder's Icons tab.
- [ ] Verify the Preview tab on home and function screens.
- [ ] Build and validate the PKG with the builder's supported packaging tools.

The Firefly atlas is source artwork only; it is not itself a PS4 theme package. The fixed filenames above are taken from `app/config.py`; do not rename them.
