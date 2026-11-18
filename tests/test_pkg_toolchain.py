"""Tests for the PS4 packaging toolchain preflight."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import pkg


class PackageToolchainTests(unittest.TestCase):
    def test_non_windows_host_is_reported(self):
        with patch.object(pkg.sys, "platform", "linux"), patch.object(
            pkg, "PKG_TOOLS_DIR", Path("/missing/tools")
        ):
            missing = pkg.missing_tool_requirements()
        self.assertIn("Windows host (the Sony packaging tools are Windows executables)", missing)
        self.assertFalse(pkg.tools_available())

    def test_every_required_file_must_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in (
                "orbis-pub-cmd.exe",
                "ext/sc.exe",
                "ext/di.exe",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"test")
            with patch.object(pkg.sys, "platform", "win32"), patch.object(
                pkg, "PKG_TOOLS_DIR", root
            ):
                self.assertEqual(pkg.missing_tool_requirements(), [])
                self.assertTrue(pkg.tools_available())
                self.assertFalse(pkg.LOUDNESS_DLL.is_file())  # optional for theme packaging

                (root / "ext/di.exe").unlink()
                self.assertEqual(pkg.missing_tool_requirements(), ["ext/di.exe"])
                self.assertFalse(pkg.tools_available())


if __name__ == "__main__":
    unittest.main()
