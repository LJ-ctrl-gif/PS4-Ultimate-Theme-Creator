"""Regression tests for the PS4 FTP browser UI wiring."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Ps4FtpUiTests(unittest.TestCase):
    def test_package_panel_exposes_read_only_ps4_ftp_browser(self):
        html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        main = (ROOT / "app/main.py").read_text(encoding="utf-8")
        self.assertIn('id="ps4-ftp-host"', html)
        self.assertIn('id="ps4-ftp-path"', html)
        self.assertIn('id="ps4-ftp-browse"', html)
        self.assertIn("Read-only", html)
        self.assertIn('api("/api/ps4/ftp/list"', js)
        self.assertIn('$("ps4-ftp-browse").addEventListener("click", browsePs4Ftp)', js)
        self.assertIn('@app.post("/api/ps4/ftp/list")', main)
        self.assertIn("ps4_ftp.list_media(host, port, path)", main)

    def test_browser_escapes_names_by_using_text_content(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        start = js.index("async function browsePs4Ftp()")
        end = js.index("\nasync function packageBuild()", start)
        browser = js[start:end]
        self.assertIn("name.textContent =", browser)
        self.assertIn("list.textContent = err.message", browser)
        self.assertNotIn("innerHTML", browser)


    def test_browser_offers_import_into_editor_slots(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        main = (ROOT / "app/main.py").read_text(encoding="utf-8")
        ftp = (ROOT / "app/ps4_ftp.py").read_text(encoding="utf-8")
        self.assertIn('api("/api/ps4/ftp/import"', js)
        self.assertIn("Import to editor", js)
        self.assertIn('slots.chosen[slotId] = imported.job_id', js)
        self.assertIn('@app.post("/api/ps4/ftp/import")', main)
        self.assertIn("ps4_ftp.download_media(host, port, path, MAX_UPLOAD_BYTES)", main)
        self.assertIn("ftp.retrbinary", ftp)
        self.assertIn("512 MB import limit", ftp)


if __name__ == "__main__":
    unittest.main()
