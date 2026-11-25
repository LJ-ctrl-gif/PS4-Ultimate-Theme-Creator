# PS4 Ultimate Theme Creator

Local web app that builds a custom PS4 theme — backgrounds, icons, animated
scene, music and sound effects — and packs it into an installable `.pkg`.

Everything runs in your browser against a server on your own machine. Nothing
is uploaded anywhere.

```powershell
.\run.ps1
```

Then open <http://127.0.0.1:8000>. The script installs the Python dependencies
if they are missing and starts the server. The interface is available in
English and Spanish.

![Preview of the console home screen](docs/03-preview-home.png)

---

## Android / Termux (phone-only setup)

The artwork editor can run locally on Android through Termux. Install the
Termux packages first:

```bash
pkg update
pkg install python python-numpy ffmpeg
```

Clone the repository, enter its folder, and start the app:

```bash
git clone https://github.com/LJ-ctrl-gif/PS4-Ultimate-Theme-Creator.git
cd PS4-Ultimate-Theme-Creator
bash run-termux.sh
```

Open <http://127.0.0.1:8000> in the phone browser. Keep Termux running while
using the editor.

### Optional phone-to-device LAN handoff

When starting `bash run-termux.sh`, answer **y** to enable LAN transfer.
The launcher prints the phone's Wi-Fi IPv4 address. Keep the phone and receiving
device on the same trusted Wi-Fi network. After exporting a theme source ZIP,
the Package tab shows a token-protected transfer URL; replace `PHONE-IP` with
the address printed by Termux and open that URL on the receiving device.

LAN mode is off by default. While it is enabled, remote devices can access only
the tokenized transfer page and that single ZIP download; the editor and its
other API routes remain blocked to remote clients. Stop the server with
Ctrl+C when finished. The ZIP is still source material, **not an installable
PS4 PKG**; copying it to a PS4 does not install a theme. If dependency installation reports a NumPy build error,
install Termux's packaged NumPy with `pkg install python-numpy`, then retry
the launcher. Android is a local artwork-editing route; it does not provide
the Windows-only proprietary PS4 package toolchain.

---

## Requirements

| | |
|---|---|
| **Python 3.10+** | `run.ps1` installs `fastapi`, `uvicorn`, `python-multipart`, `numpy` |
| **ffmpeg** + **ffprobe** on PATH | decode the input video and audio |
| Windows | the packaging tools are 32-bit `.exe` |

ImageMagick is not needed — the DXT1a compressor is part of the project. If
`magick` is on PATH it is offered as an alternative backend.

### The packaging tools are not bundled

The package builder depends on proprietary Sony publishing executables. They
are intentionally not included in this repository and must not be redistributed
without authorization.

The three files required by the current package preflight are:

| Required file | Destination |
|---|---|
| `orbis-pub-cmd.exe` | `tools/` |
| `ext/sc.exe` | `tools/ext/` |
| `ext/di.exe` | `tools/ext/` |

Optional audio helpers:

| Optional file | Destination | Purpose |
|---|---|---|
| `ext/libatrac9.dll` | `tools/ext/` | ATRAC9 loudness measurement |
| `at9tool.exe` | `tools/` | Convert uploaded music to `.at9` |

Obtain proprietary tools only through an authorized source and comply with
their applicable license terms. Do not commit these executables to a public
repository. The project can still generate and export the BLACK VOID artwork
bundle without them, but it cannot produce an installable PS4 `.pkg`.

### Remote Windows preflight

The repository includes **BLACK VOID Windows Packaging Preflight** under
GitHub Actions. On a phone, open the
[Actions page](https://github.com/LJ-ctrl-gif/PS4-Ultimate-Theme-Creator/actions),
select that workflow, and tap **Run workflow**. It checks whether the three
required executables are present in the checked-out `tools/` folder and
uploads a short report. This is only a prerequisite check; it does not build
a package or supply proprietary tools.

The app itself can still be used for artwork preparation and ZIP export when
the packaging tools are absent.
---

## What it makes

| Tab | What it customises | Slots |
|---|---|---|
| Background | **still image** (home, top menu, thumbnail, icon) or **animated** (video/gif → RAF scene) | 4 |
| Icons | function (128×128 + 152×152 glow) and content (512×512) | 9 + 10 |
| Sounds | menu music → `.at9` · effects → `.vag` | 1 + 3 |
| Preview | mock-up of the console screens with your images | — |
| Package | puts it all into a `.pkg` | — |

**23 independent image slots.** The only required one is the **home
background**; every other background copies from it when left empty, and icons
you don't upload keep the system ones.

![Background tab](docs/01-background.png)

![Icons tab](docs/02-icons.png)

## Mock PKG test mode

The Package tab also includes **Run Mock PKG Test** for browser and phone
development when the real packaging executables are unavailable. It runs the
normal theme source assembly, checks the generated asset inventory and
integrity manifest, and reports the packaging stages as simulated.

Mock mode is a development check only. It deliberately does **not** create a
fake .pkg, a bootable package, or a file that can be installed on a PS4.
The real **Build PKG** action remains gated by the required authorized
packaging toolchain.

## Theme source ZIP export

The Package tab includes **Export theme source ZIP**. It assembles the selected
backgrounds, icons, optional audio, and optional animated scene into their
theme content paths, then adds a SHA-256 manifest. The archive is useful for
transferring or backing up the assembled source tree.

**It is not an installable PS4 PKG.** The source ZIP does not contain generated
package metadata or the proprietary publishing output. Installing a theme
still requires a supported, authorized packaging environment.

## BLACK VOID preset import

The generated `BLACK-VOID-theme-assets.zip` can be imported into a running
local builder without uploading the 23 images individually. Send the ZIP to
`POST /api/preset/black-void/import` as multipart field `file`. The endpoint
validates the archive and image set, creates the normal image-slot jobs, and
returns the slot-to-job-ID map needed by `POST /api/package/build`.

Example:

```bash
curl -F "file=@BLACK-VOID-theme-assets.zip" \
  http://127.0.0.1:8000/api/preset/black-void/import
```

The import prepares artwork only. The Package tab still requires the
project's supported packaging environment before an installable PS4 `.pkg`
can be produced.

---

## How it works

**Still and animated backgrounds are mutually exclusive.** With a
`scene/background.raf/` present the console paints the scene on *both* screens,
so the two still PNGs are never visible — they are left out of the package. The
tab makes this an explicit choice: pick *animated* and the top-menu background
disappears, while the home one is renamed *theme image*, which is what it
actually does there (the list thumbnail, the icon and the store shot come from
it).

**Audio is converted for you.** Upload any format and it becomes what the
console expects. The music also has a **volume control**: a normal song lands
about 13 dB above the music of a real theme, so without levelling it drowns out
the rest of the system. The resulting level is declared in `param.sfo` as
`bgmhome_loud`, which is what the console uses to balance it.

**The preview** builds the three screens a theme touches — home, top menu and
the *apply theme* screen — using your images, icons and colours, so you can
check contrast without a package → USB → install round trip. Positions are
measured from real console captures.

![Apply theme screen](docs/04-preview-apply.png)

**Work survives a page reload.** File ids are kept in the browser and checked
against `workspace/` on startup; whatever is still alive is restored.

Animated mode also exports a standalone `.zip` with the
`scene/background.raf/` folder, in case you'd rather assemble the theme by hand.

---

## Theme format

What the console produces from your assets:

```
Image0/
  theme.xml                              descriptor
  texture/
    background/homescreen.png            1920×1080  ┐ only when there is
    background/functionscreen.png        1920×1080  ┘ no animated scene
    preview.png                          740×416    list thumbnail
    function_icon/<name>.png             128×128
    function_icon/<name>_glow.png        152×152
    content_icon/<name>.png              512×512
  scene/background.raf/                  animated background (optional)
    NN.dds                               DXT1a
    plane.mdx                            shared plane
    index.xml                            scene
  sound/bgm_home.at9                     menu music (optional)
  sound/se_{decide,cursor,cancel}.vag    sound effects (optional)
Sc0/  param.sfo · icon0.png 512×512 · pic1.png   (placed by the tool)
```

Paths are not configurable — the console looks for those literal names.
Valid function icons: `community`, `event`, `friend`, `message`,
`notification`, `party`, `power`, `setting`, `trophy`.

![Package tab](docs/05-package.png)

### Rules you cannot break

All of these were verified on a real console. The app enforces them, so you
shouldn't be able to hit them from the interface — but if you touch the code,
they are what will bite.

| Rule | What happens otherwise |
|---|---|
| `volume_type=pkg_ps4_theme` + `IRO_TAG=2` + `CATEGORY=ac` | Without `IRO_TAG` it installs as an app with a *Start* button and throws **CE-37695-0**. With `CATEGORY=gd` it shows up in *Themes* but the console crashes (**CE-36329-3**) |
| `theme.xml` at the root, with `format-version` and `themecolor` | the console crashes when applying the theme |
| `background.raf/`: **≤ 6 MiB** of `.dds` **and** **≤ 48 frames** | installs fine, then fails to apply with **CE-38196-7** "data corrupted" |
| The scene's `wait` is in **seconds with decimals** | `wait="2"` is 2 seconds per frame, not 200 ms |
| The `.at9` is **144 kbps** with a loop (`-wholeloop`) | at 168 kbps and without an `smpl` chunk it stays silent, even though ffmpeg reads it fine |
| `<homebgm-enable>` only `True` when `sound/bgm_home.at9` exists | `True` without music makes the console play its own |
| Passcode of 32 zeros | it encrypts the package and is **not stored inside it**, so the installer has to know it up front |

Two more traps worth knowing: `gdt` is **not** a valid category despite what
some tutorials say, and the RAF scene has **no `target=` attribute** — the
`<case wait target>` you'll find online is made up.

Because of the frame and weight caps, the resolution you pick decides how long
the animation can be: **13** frames at 1280×720, **24** at 960×540, **48** at
640×360. DXT1 is fixed-rate, so the weight does not depend on the image.

---

## Development

```
app/
  config.py     format constants, limits and theme paths
  dxt1.py       DXT1a (BC1) encoder/decoder in numpy + .dds header
  dds.py        compression backends (native / ImageMagick)
  media.py      ffmpeg and ffprobe wrappers
  mdx.py        .mdx model (XDM format): parse, build, plane generator
  raf.py        animated scene (index.xml)
  vag.py        VAG (PS-ADPCM) encoder for the sound effects
  at9.py        ATRAC9 conversion via at9tool (optional)
  theme_xml.py  the theme.xml
  theme.py      frame names, LF-forced writing, .zip assembly
  pkg.py        packaging: param.sfo, keystone, .gp4, img_create
  jobs.py       working folders under workspace/
  main.py       API and server
  static/       interface (html, css, js — no bundler, no build step)
tests/          10 suites + make_fixtures.py
tools/          drop the packaging binaries here (not included)
workspace/      uploads and outputs, temporary — cleans itself
```

The frontend has no build step: edit `app/static/*` and reload.

### Tests

They need the server running on port 8000, and the browser ones need
playwright.

```powershell
python -m playwright install chromium    # only for test_ui*
python tests\make_fixtures.py            # sample.mp4 / .png / .at9 ... via ffmpeg
$env:PYTHONIOENCODING = "utf-8"

python tests\test_dxt1.py                # DXT1a encoder
python tests\test_http.py                # animated background API
python tests\test_slots.py               # slots and package tree
python tests\test_theme.py               # param.sfo read from inside the .pkg
python tests\test_pkg.py                 # packaging validation
python tests\test_audio.py               # music and effects
python tests\test_convert.py             # standalone converter
python tests\test_ui.py                  # browser: player and sliders
python tests\test_ui_slots.py            # browser: slot grids and packaging
python tests\test_ui_preview.py          # browser: console mock-up and session
```

Each suite prints `OK`/`FAIL` per line and exits 1 if anything failed. The ones
that build a `.pkg` need the tools in `tools/`.

---

## Licence and credits

The code in this repository is MIT — see [LICENSE](LICENSE). That does **not**
cover the packaging binaries, which are proprietary Sony software and are not
distributed here.

Tool by [Imxnxl](https://github.com/Imxnxl).
