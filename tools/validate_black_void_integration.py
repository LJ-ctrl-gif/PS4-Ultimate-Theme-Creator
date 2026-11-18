"""Cross-check the BLACK VOID bundle against the live app's slot contract."""
from __future__ import annotations

import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import IMAGE_SLOTS  # noqa: E402
from app.main import app  # noqa: E402

BUNDLE = ROOT / "dist" / "BLACK-VOID-theme-assets.zip"
JS = ROOT / "app" / "static" / "app.js"
HTML = ROOT / "app" / "static" / "index.html"

with ZipFile(BUNDLE) as archive:
    names = set(archive.namelist())
    for slot_id, spec in IMAGE_SLOTS.items():
        member = (
            "Sc0/sce_sys/icon0.png" if slot_id == "icon0"
            else f"Image0/{spec['path']}"
        )
        assert member in names, f"Missing app slot asset: {member}"
        assert archive.getinfo(member).file_size > 0, f"Empty app slot asset: {member}"

routes = {
    (route.path, frozenset(getattr(route, "methods", None) or ()))
    for route in app.routes if hasattr(route, "path")
}
assert any(
    path == "/api/preset/black-void/import" and "POST" in methods
    for path, methods in routes
), "BLACK VOID import API route is not registered"

js = JS.read_text(encoding="utf-8")
html = HTML.read_text(encoding="utf-8")
assert "/api/preset/black-void/import" in js, "Browser uploader does not call the import API"
assert "importBlackVoidPreset" in js, "Browser import handler is missing"
assert 'id="black-void-file"' in html, "BLACK VOID file input is missing"

print(f"BLACK VOID integration OK: {len(IMAGE_SLOTS)} app slots, API route, and browser import UI.")
