"""Safe workspace inventory and single-item deletion tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import jobs


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)

    def test_lists_job_metadata_without_paths_and_deletes_one_job(self):
        with patch.object(jobs, "WORKSPACE", self.workspace):
            job = jobs.create("slot", "wallpaper.png", b"image-data")
            items = jobs.list_recent()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["id"], job.id)
            self.assertEqual(items[0]["kind"], "slot")
            self.assertEqual(items[0]["name"], "wallpaper.png")
            self.assertGreaterEqual(items[0]["size_bytes"], len(b"image-data"))
            self.assertNotIn("root", items[0])
            self.assertTrue(jobs.delete("slot", job.id))
            self.assertEqual(jobs.list_recent(), [])

    def test_rejects_unknown_kind_and_invalid_identifier(self):
        with patch.object(jobs, "WORKSPACE", self.workspace):
            job = jobs.create("slot", "icon.png", b"png")
            self.assertFalse(jobs.delete("../slot", job.id))
            self.assertFalse(jobs.delete("slot", "../job.json"))
            self.assertIsNotNone(jobs.load("slot", job.id))


if __name__ == "__main__":
    unittest.main()
