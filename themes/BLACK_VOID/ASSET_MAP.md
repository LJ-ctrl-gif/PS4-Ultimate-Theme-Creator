# BLACK VOID — PS4 theme asset map

Visual direction: **true jet black (#000000)** across the background, with restrained brushed-silver light trails and crisp silver icon silhouettes. Do not use charcoal or graphite as the background fill.

## Background artwork

Both background images have been generated in Adobe Firefly, resized to 1920x1080 PNG, and previewed.

| Target path | Artwork | Source |
|---|---|---|
| `texture/background/homescreen.png` | Jet-black home background with subtle silver edge trails | [PNG artwork](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:02f71d3a-777f-4641-91f1-d6ae11e2cc6a) |
| `texture/background/functionscreen.png` | Jet-black function background with silver edge trails and a clear center | [PNG artwork](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:b5779301-d818-42c8-959b-8be4e83d4736) |

These are source artwork links, not repository files yet. The GitHub text-file connector cannot upload binary PNG bytes, so do not treat the images as installed theme assets until they are transferred through the builder's asset upload flow.

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

- [ ] Transfer the two background PNGs into the builder's Background tab.
- [ ] Export nine function icons at 128x128 and their glow variants at 152x152.
- [ ] Export ten content icons at 512x512.
- [ ] Preserve transparency and use consistent silver styling against jet black.
- [ ] Verify the Preview tab on home and function screens.
- [ ] Build and validate the PKG with the builder's supported packaging tools.

The backgrounds are prepared artwork only; they are not yet committed as binary files or installed in a PS4 theme package. The fixed icon filenames above are taken from `app/config.py`; do not rename them.
