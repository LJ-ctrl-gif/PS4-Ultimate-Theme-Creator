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

### Resized working previews

The following links are resized working crops, not final installed assets. Some use transparent/empty padding to preserve the full source icon; inspect them in the builder before final use.

| Icon | Size | Working PNG |
|---|---:|---|
| Community | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:311c49e6-9f57-46c3-9158-1a982a319b02) |
| Events | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:2ff50038-d9c5-4055-9506-56ceb3bab176) |
| Friends | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:426d9837-5ef0-434d-98fa-2e28f21adafa) |
| Messages | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:924fc291-14df-4888-9415-ed55e7835dde) |
| Notifications | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:cdfc3676-e0ea-416d-b8cd-4cb516a06d04) |
| Party | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:6518e9e8-82bc-4f72-a1b9-e6e6dec842aa) |
| Power | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:2a4fc605-bc94-4ef8-816d-fdb24a9ba9bd) |
| Settings | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:0fd81cd6-312c-4968-a9f4-97e39706e536) |
| Trophies | 128x128 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:d73b4491-a343-4630-8739-e3e754c4af20) |

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

### Resized working previews

These are 512x512 working crops, not yet visually approved or installed.

| Icon | Size | Working PNG |
|---|---:|---|
| Browser | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5baf9a0c-b211-4f3e-9cd1-5a216e42403c) |
| Disc | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:d9ad8352-823a-4498-9753-9f33416737b1) |
| Disc overlay | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5f395e13-f5f1-41a1-acdc-a58e29fe7e84) |
| Folder | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:8e4f3e8e-02ce-4263-b7a1-b95a3694403f) |
| Gallery | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:489d3f26-6f73-4710-b711-f3cf097f52f5) |
| Library | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:9e60b327-613e-4e9c-87f2-de378e355528) |
| Live from PlayStation | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:bb47dbaf-c25c-46c9-9dcf-d81bcac0b148) |
| Share Play | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:f4f20206-b3f8-4f04-80d9-8f69d4a0e796) |
| TV / Video | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:f6eb9293-3fa7-48d7-abe9-ca6bb9b19e0d) |
| USB Music | 512x512 | [Preview](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:dc7212f2-948d-4b16-931d-85daf5f59185) |

## Integration checklist

- [ ] Transfer the two background PNGs into the builder's Background tab.
- [ ] Review all nine function icon crops and refine padding/cropping where needed.
- [ ] Export nine function icons at 128x128 and their glow variants at 152x152.
- [ ] Review and finalize ten content icons at 512x512.
- [ ] Preserve transparency and use consistent silver styling against jet black.
- [ ] Verify the Preview tab on home and function screens.
- [ ] Build and validate the PKG with the builder's supported packaging tools.

The backgrounds and icon crops are prepared artwork only; they are not yet committed as binary files or installed in a PS4 theme package. The fixed icon filenames above are taken from `app/config.py`; do not rename them.
