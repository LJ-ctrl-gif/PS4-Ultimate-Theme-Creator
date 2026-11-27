"""Regression checks for the browser's explicitly non-installable mock PKG mode."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MockPackageUiTests(unittest.TestCase):
    def test_mock_button_is_present_and_disclosed(self):
        html = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
        self.assertIn('id="pkg-mock-build"', html)
        self.assertIn("does not create an installable PKG", html)

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


    def test_source_export_ui_escapes_server_values(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        self.assertIn("function escapeHtml(value)", js)
        self.assertIn("escapeHtml(item.asset)", js)
        self.assertIn("escapeHtml(result.archive_name)", js)
        self.assertIn("escapeHtml(result.download)", js)
        self.assertIn("+ result.transfer_path", js)
        self.assertIn('$("theme-transfer-url").textContent = transferUrl', js)



    def test_lan_transfer_shows_exact_host_link_and_copy_action(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        start = js.index("async function exportThemeSource()")
        end = js.index("\nasync function packageBuild()", start)
        export = js[start:end]
        self.assertIn('id="theme-transfer-url"', export)
        self.assertIn('id="theme-transfer-copy"', export)
        self.assertIn('id="theme-transfer-host"', export)
        self.assertIn('location.hostname === "localhost"', export)
        self.assertIn('hostInput.addEventListener("input", makeTransferUrl)', export)
        self.assertIn('$("theme-transfer-copy").disabled = !transferUrl', export)
        self.assertIn('location.hostname', export)
        self.assertIn('navigator.clipboard.writeText(transferUrl)', export)
        self.assertIn('$("theme-transfer-url").textContent = transferUrl', export)
        self.assertIn("temporary link exposes only this ZIP", export)

    def test_real_package_result_escapes_server_values(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        start = js.index("async function packageBuild()")
        end = js.index("\nasync function mockPackageBuild()", start)
        build = js[start:end]
        self.assertIn("escapeHtml(i.asset)", build)
        self.assertIn("escapeHtml(s.label)", build)
        self.assertIn("escapeHtml(parts[1] || parts[0])", build)
        self.assertIn("escapeHtml(s.seconds)", build)
        self.assertIn("escapeHtml(r.pkg_name)", build)
        self.assertIn("href=\"${escapeHtml(r.download)}\"", build)

    def test_catalogue_and_backend_values_are_escaped(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        self.assertIn("const lblHtml = (x) => escapeHtml(lbl(x))", js)
        start = js.index("function slotCard(spec)")
        end = js.index("\nfunction pintarSlots()", start)
        slot = js[start:end]
        self.assertIn("lblHtml(spec.label)", slot)
        self.assertIn("escapeHtml(spec.fallback)", slot)
        self.assertIn("escapeHtml(spec.file)", slot)
        colors_start = js.index("function pintarColoresDelSistema()")
        colors_end = js.index("\n/** <input type=color>", colors_start)
        colors = js[colors_start:colors_end]
        self.assertIn("escapeHtml(c.value)", colors)
        self.assertIn("lblHtml(c.label)", colors)
        self.assertIn('escapeHtml(sys.default_backend)', js)
        self.assertIn('escapeHtml(b)', js)

    def test_mock_failure_is_shown_inline_and_as_text(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        start = js.index("async function mockPackageBuild()")
        end = js.index("\nasync function bootPackage()", start)
        mock = js[start:end]
        self.assertIn('panel.replaceChildren()', mock)
        self.assertIn('detail.setAttribute("role", "alert")', mock)
        self.assertIn('detail.textContent = `Source assembly failed: ${err.message}`', mock)


    def test_source_actions_are_not_blocked_by_pkg_defaults(self):
        js = (ROOT / "app/static/app.js").read_text(encoding="utf-8")
        boot_start = js.index("async function bootPackage()")
        boot_end = js.index("/* ------------------------------------------------------------------ idioma */", boot_start)
        boot_package = js[boot_start:boot_end]
        self.assertNotIn('$("pkg-mock-build").addEventListener', boot_package)
        self.assertNotIn('$("theme-source-export").addEventListener', boot_package)
        listener_start = js.index("/* ------------------------------------------------------------ listeners */")
        self.assertGreater(js.index('$("pkg-mock-build").addEventListener', listener_start), listener_start)
        self.assertGreater(js.index('$("theme-source-export").addEventListener', listener_start), listener_start)


if __name__ == "__main__":
    unittest.main()
