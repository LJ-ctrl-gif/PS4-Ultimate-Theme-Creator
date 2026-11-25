"""Regression checks for the browser's explicitly non-installable mock PKG mode."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MockPackageUiTests(unittest.TestCase):
    def test_mock_button_is_present_and_disclosed(self):
        html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        self.assertIn('id="pkg-mock-build"', html)
        self.assertIn("does not create an installable PS4 PKG", html)

    def test_mock_assembles_source_and_never_claims_a_pkg(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        start = js.index("async function mockPackageBuild()")
        end = js.index("\nasync function bootPackage()", start)
        mock = js[start:end]
        self.assertIn('"/api/theme-source/export"', mock)
        self.assertIn('["Binary .pkg generation", "SKIPPED"]', mock)
        self.assertIn("No PS4 PKG was generated", mock)
        self.assertIn("Download source ZIP (not installable)", mock)
        self.assertNotIn("pkg-build", mock)


if __name__ == "__main__":
    unittest.main()
