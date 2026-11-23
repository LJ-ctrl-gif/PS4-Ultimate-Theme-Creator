"""Tests for export of an assembled theme source ZIP without PKG tools."""
from __future__ import annotations

import asyncio
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app import jobs, main


class ThemeSourceExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)

    def fake_collect(self, _slots, _settings, content_dir, **_kwargs):
        content_dir.mkdir(parents=True, exist_ok=True)
        (content_dir / "theme.xml").write_text("<theme/>", encoding="utf-8")
        icon = content_dir / "texture" / "function_icon" / "setting.png"
        icon.parent.mkdir(parents=True)
        icon.write_bytes(b"sample-icon")
        return [{"asset": "Theme descriptor", "path": "theme.xml", "bytes": 8}]

    def test_exports_transfer_zip_without_package_toolchain(self):
        home = SimpleNamespace(id="home-job")
        with (
            patch.object(jobs, "WORKSPACE", self.workspace),
            patch.object(main, "_resolve_slot_jobs", return_value={"home": home}),
            patch.object(main, "_collect_theme_assets", side_effect=self.fake_collect),
        ):
            result = asyncio.run(main.theme_source_export(
                title="BLACK VOID",
                slots="{}",
                animated_job="",
                audio_job="",
                sfx="{}",
                frames=24,
                wait_seconds=0.1,
                backend=main.DEFAULT_BACKEND,
                themecolor=0,
                fontcolor=main.theme_xml.DEFAULTS["fontcolor"],
                fontshadowcolor=main.theme_xml.DEFAULTS["fontshadowcolor"],
                focuscolor=main.theme_xml.DEFAULTS["focuscolor"],
            ))
            response = main.theme_source_download(result["job_id"])

        self.assertFalse(result["installable"])
        self.assertGreater(result["archive_bytes"], 0)
        with zipfile.ZipFile(response.path) as archive:
            names = set(archive.namelist())
            self.assertIn("theme.xml", names)
            self.assertIn("texture/function_icon/setting.png", names)
            self.assertIn("TRANSFER-README.txt", names)
            self.assertIn("TRANSFER-MANIFEST.json", names)
            self.assertIn("MANIFEST.sha256", names)
            readme = archive.read("TRANSFER-README.txt").decode("utf-8")
            self.assertIn("NOT an installable PS4 PKG", readme)
            self.assertIn("USB drive", readme)
            transfer = __import__("json").loads(archive.read("TRANSFER-MANIFEST.json"))
            self.assertFalse(transfer["installable"])
            self.assertGreaterEqual(transfer["file_count"], 3)
            records = {item["path"]: item for item in transfer["files"]}
            self.assertIn("theme.xml", records)
            self.assertEqual(
                records["theme.xml"]["sha256"],
                __import__("hashlib").sha256(archive.read("theme.xml")).hexdigest(),
            )
            manifest = archive.read("MANIFEST.sha256").decode("utf-8")
            self.assertIn("theme.xml", manifest)
            self.assertIn("TRANSFER-MANIFEST.json", manifest)

    def test_rejects_export_without_home_background(self):
        with patch.object(main, "_resolve_slot_jobs", return_value={}):
            with self.assertRaises(HTTPException) as caught:
                asyncio.run(main.theme_source_export(
                    title="BLACK VOID", slots="{}", animated_job="",
                    audio_job="", sfx="{}", frames=24,
                    wait_seconds=0.1, backend=main.DEFAULT_BACKEND,
                    themecolor=0,
                    fontcolor=main.theme_xml.DEFAULTS["fontcolor"],
                    fontshadowcolor=main.theme_xml.DEFAULTS["fontshadowcolor"],
                    focuscolor=main.theme_xml.DEFAULTS["focuscolor"],
                ))
        self.assertEqual(caught.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
