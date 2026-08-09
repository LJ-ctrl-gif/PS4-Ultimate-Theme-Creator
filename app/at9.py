"""ATRAC9 (.at9) conversion through at9tool, when it is available.

ATRAC9 is proprietary and cannot be generated with what ships here: ffmpeg
decodes it but does not encode it, and the official encoder lives inside
`tools/ext/libatrac9.dll`, which is 32-bit with an undocumented ABI
(`sceAt9GetVersion` and `sceAt9GetHandle` do answer from a 32-bit process,
but the configuration calls want structs whose layout is not published).

The practical route is `at9tool.exe`, the official SDK converter. It is not
bundled: drop it in `tools/` and the app converts on its own, otherwise the
`.at9` has to be uploaded already made.

The syntax came from ATRACTool-Reloaded (MIT), the parameters did NOT: they
are copied from a theme that actually plays on the console.

    at9tool -e -br 144 -fs 48000 -wholeloop  input.wav  output.at9
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import PKG_TOOLS_DIR, PROJECT_ROOT
from .media import NO_WINDOW, MediaError

#: Possible names. There is a PS4 and a PSVita build; the PS4 one is the good one.
TOOL_NAMES = ("ps4_at9tool.exe", "at9tool.exe")

#: 144 kbps, measured on the bgm_home.at9 of a theme that DOES play on the
#: console: 18000 B/s, block align 384, configData fe 74 0b f0.
#: This used to be 168, which is ATRACTool-Reloaded's default and comes from no
#: PS4 theme: it gives align 448 and configData fe 74 0d f0. The music stayed
#: silent with that.
DEFAULT_BITRATE = 144
SAMPLE_RATE = 48000

#: A theme needs no more; keeps waits short and packages small.
MAX_SECONDS = 300


def find_tool() -> Path | None:
    """Looks for at9tool in tools/, tools/ext/, the project root and PATH."""
    for folder in (PKG_TOOLS_DIR, PKG_TOOLS_DIR / "ext", PROJECT_ROOT):
        for name in TOOL_NAMES:
            candidate = folder / name
            if candidate.is_file():
                return candidate
    for name in TOOL_NAMES:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def available() -> bool:
    return find_tool() is not None


def encode(wav_path: Path, dest: Path, bitrate: int = DEFAULT_BITRATE) -> Path:
    """WAV PCM -> .at9. Needs at9tool; raises MediaError when missing."""
    tool = find_tool()
    if tool is None:
        raise MediaError(
            "at9tool was not found. Drop it in tools/ to convert automatically, "
            "or upload the file already in .at9."
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()

    proc = subprocess.run(
        [
            str(tool), "-e",
            "-br", str(bitrate),
            "-fs", str(SAMPLE_RATE),
            # Menu music loops. The reference theme carries an smpl chunk with
            # playCount=0 (infinite); without -wholeloop none is written and the
            # file comes out with no loop point.
            "-wholeloop",
            str(wav_path), str(dest),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=600, creationflags=NO_WINDOW,
    )
    if not dest.is_file() or dest.stat().st_size == 0:
        tail = proc.stdout.decode("utf-8", "replace").strip().splitlines()
        raise MediaError("at9tool produced no file: " + ("\n".join(tail[-4:]) or "no output"))
    return dest
