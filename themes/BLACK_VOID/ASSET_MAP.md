# BLACK VOID — PS4 theme asset map

Visual direction: **jet black (#000000)** with restrained brushed-silver iconography and silver edge lighting.

## Background artwork

| Target path | Artwork |
|---|---|
| `texture/background/homescreen.png` | [1920x1080 PNG](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:02f71d3a-777f-4641-91f1-d6ae11e2cc6a) |
| `texture/background/functionscreen.png` | [1920x1080 PNG](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:b5779301-d818-42c8-959b-8be4e83d4736) |

These are artwork links, not binary files committed to this repository.

## Function icons

Builder slots and exact filenames from `app/config.py`. Standard icons are 128x128 PNG; glow variants must be 152x152 PNG.

| Slot | Filename | Standard PNG |
|---|---|---|
| fn:community | community.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:3e15042d-ebdf-40cc-8f9e-7c71297afcda) |
| fn:event | event.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:2dfa9bc6-a9b6-435e-b428-b74bfec4854a) |
| fn:friend | friend.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:c26ca465-d5b0-475a-bfe5-c2a2d96d3234) |
| fn:message | message.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:81430e5f-d0ea-4266-be94-aa0b7fece25b) |
| fn:notification | notification.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:96095470-526c-44b4-ae27-8c898ae33018) |
| fn:party | party.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:b5f76dd4-7bb5-4b9a-b005-326503696fc0) |
| fn:power | power.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:a8b1abd1-b935-420c-87ac-a6f89cbdc825) |
| fn:setting | setting.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:956e08b1-5fbd-4ebd-a1bf-6dbc5c4e3b2a) |
| fn:trophy | trophy.png | [128x128](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:1c50f2b4-7339-4d11-b850-222e3b9d63ea) |

Glow filenames use `_glow` before the extension (for example, `power_glow.png`). Glow files are **not yet generated**.

## Content icons

All content icons are 512x512 PNG.

| Slot | Filename | PNG |
|---|---|---|
| ct:browser | browser.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:dc1c5d5a-75d3-4707-9c5e-4a3edcd0810d) |
| ct:disc | disc.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5e8bd3f9-54e0-4156-8d3e-c25c18d23368) |
| ct:discoverlay | discoverlay.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:5639f83f-f743-4d3e-a7da-7806b5c57748) |
| ct:folder | folder.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:82c0b9e3-5e4a-4005-851b-af925c06d4b1) |
| ct:gallery | gallery.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:c199133a-aa1e-4124-9ba3-413dfa30d4da) |
| ct:library | library.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:0aec1794-48d6-4eff-8b3b-9110fcaa33a7) |
| ct:livefromps | livefromps.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:6074ea6c-68a8-43e2-9bf8-7e986bc9c96f) |
| ct:shareplay | shareplay.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:d7ffa59d-0863-4905-a44b-dabb59934629) |
| ct:tvvideo | tvvideo.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:363cb601-b4b9-46e6-85c7-b53d484e4f5a) |
| ct:usbmusic | usbmusic.png | [512x512](https://photoshop-api.adobe.io/v2/short-url/urn:aaid:ps:US:acbdb8a5-9c2e-4434-a17c-e2f7dc9b4875) |

## Status and remaining work

- [x] Generate the two background artworks.
- [x] Crop all 9 function icons and resize to 128x128.
- [x] Crop all 10 content icons and resize to 512x512.
- [ ] Visually inspect every icon in the builder; the resized images currently preserve the full tall crop using transparent side padding.
- [ ] Create 9 matching 152x152 glow variants.
- [ ] Transfer the binary PNGs into the builder and verify both screens.
- [ ] Build and validate a PS4 theme package using the builder's supported packaging tools.

**Important:** the links above point to Adobe-hosted PNG outputs. They are not committed binary assets, not yet installed in a theme, and not proof of a working PS4 PKG.