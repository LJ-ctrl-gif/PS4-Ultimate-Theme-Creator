"""Tests for the BLACK VOID preset import transaction."""
from __future__ import annotations

import asyncio
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from starlette.datastructures import UploadFile

from app import jobs, main, media
from app.config import IMAGE_SLOTS


def make_archive() -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for slot_id, spec in IMAGE_SLOTS.items():
            member = (
                "Sc0/sce_sys/icon0.png" if slot_id == "icon0"
                else f"Image0/{spec['path']}"
            )
            archive.writestr(member, b"fake-png-data")
    return out.getvalue()


class FakeJob:
    def __init__(self, root: Path, job_id: str, filename: str, data: bytes):
        self.id = job_id
        self.root = root
        self.source = root / filename
        self.original_name = filename
        self.meta = {}
        self.preview_dir = root / "preview"
        self.preview_dir.mkdir(parents=True)
        self.out_dir = root / "out"
        self.out_dir.mkdir()

    def save(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.source.write_bytes(b"source")


class BlackVoidImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.created: list[FakeJob] = []
        self.counter = 0

    def fake_create(self, kind, filename, data):
        self.counter += 1
        root = self.root / f"{kind}-{self.counter}"
        root.mkdir()
        job = FakeJob(root, f"job{self.counter}", filename, data)
        job.source.write_bytes(data)
        self.created.append(job)
        return job

    @staticmethod
    def fake_probe(_path):
        return SimpleNamespace(width=512, height=512)

    @staticmethod
    def fake_render(_src, dest, _size):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"preview")
        return dest

    def invoke(self):
        upload = UploadFile(
            filename="black-void.zip",
            file=io.BytesIO(make_archive()),
        )
        return asyncio.run(main.black_void_preset_import(upload))

    def test_import_creates_jobs_for_every_slot(self):
        with (
            patch.object(jobs, "create", side_effect=self.fake_create),
            patch.object(media, "probe", side_effect=self.fake_probe),
            patch.object(media, "render_image", side_effect=self.fake_render),
        ):
            result = self.invoke()

        self.assertEqual(result["preset"], "BLACK VOID")
        self.assertEqual(result["imported"], len(IMAGE_SLOTS))
        self.assertEqual(set(result["slots"]), set(IMAGE_SLOTS))
        self.assertTrue(all((job.preview_dir / "preview.webp").is_file()
                            for job in self.created))

    def test_failed_image_rolls_back_all_created_jobs(self):
        def fail_on_second(_path):
            if len(self.created) >= 2:
                raise media.MediaError("invalid image")
            return self.fake_probe(_path)

        with (
            patch.object(jobs, "create", side_effect=self.fake_create),
            patch.object(media, "probe", side_effect=fail_on_second),
            patch.object(media, "render_image", side_effect=self.fake_render),
        ):
            with self.assertRaises(main.HTTPException) as caught:
                self.invoke()

        self.assertEqual(caught.exception.status_code, 422)
        self.assertGreaterEqual(len(self.created), 2)
        self.assertTrue(all(not job.root.exists() for job in self.created))


if __name__ == "__main__":
    unittest.main()
