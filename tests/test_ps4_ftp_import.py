"""Regression tests for GoldHEN FTP media import endpoint routing."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app import main


class Ps4FtpImportEndpointTests(unittest.TestCase):
    def invoke(self, kind, slot_id, path):
        return main.ps4_ftp_import(
            "192.168.1.23", 2121, path, kind, slot_id, 0.0
        )

    def test_invalid_destinations_are_rejected_before_download(self):
        cases = (
            ("image", "not-a-slot", "/user/icon.png", 404),
            ("audio", "not-a-slot", "/user/tone.wav", 404),
            ("video", "bgm", "/user/clip.mp4", 422),
            ("unknown", "slot", "/user/file.png", 422),
            ("image", next(iter(main.IMAGE_SLOTS)), "/user/archive.zip", 415),
        )
        with patch.object(main.ps4_ftp, "download_media") as download:
            for kind, slot_id, remote_path, status in cases:
                with self.subTest(kind=kind, slot=slot_id, path=remote_path):
                    with self.assertRaises(HTTPException) as caught:
                        self.invoke(kind, slot_id, remote_path)
                    self.assertEqual(caught.exception.status_code, status)
            download.assert_not_called()

    def make_job(self, root, filename):
        root.mkdir(parents=True, exist_ok=True)
        source = root / filename
        source.write_bytes(b"media")
        preview_dir = root / "preview"
        preview_dir.mkdir()
        return SimpleNamespace(
            id="test-job", source=source, original_name=filename,
            meta={}, preview_dir=preview_dir, save=lambda: None,
        )

    def test_image_import_creates_slot_preview(self):
        slot_id = next(iter(main.IMAGE_SLOTS))
        with tempfile.TemporaryDirectory() as temp:
            job = self.make_job(Path(temp) / "image", "icon.png")

            def render(_source, destination, _size):
                destination.write_bytes(b"preview")
                return destination

            with (
                patch.object(main.ps4_ftp, "download_media", return_value=("icon.png", b"png")) as download,
                patch.object(main.jobs, "create", return_value=job),
                patch.object(main.media, "probe", return_value=SimpleNamespace(width=512, height=512)),
                patch.object(main.media, "render_image", side_effect=render),
            ):
                result = self.invoke("image", slot_id, "/user/icon.png")

            self.assertEqual(result["kind"], "image")
            self.assertEqual(result["slot"], slot_id)
            self.assertEqual(result["job_id"], "test-job")
            self.assertEqual(result["source"]["name"], "icon.png")
            download.assert_called_once()

    def test_audio_import_routes_to_audio_processor(self):
        with (
            patch.object(main.ps4_ftp, "download_media", return_value=("effect.wav", b"wav")) as download,
            patch.object(main.jobs, "create", return_value=SimpleNamespace(id="audio-job")),
            patch.object(main, "_procesar_audio", return_value={"kind": "audio", "job_id": "audio-job"}) as process,
            patch.object(main.at9, "available", return_value=False),
        ):
            result = self.invoke("audio", "se_decide", "/user/effect.wav")

        self.assertEqual(result, {"kind": "audio", "job_id": "audio-job"})
        self.assertEqual(process.call_args.args[1], main.AUDIO_SLOTS["se_decide"])
        download.assert_called_once()

    def test_video_import_routes_to_animated_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            job = self.make_job(Path(temp) / "video", "clip.mp4")
            expected = {"kind": "video", "job_id": "video-job"}
            job.id = "video-job"
            with (
                patch.object(main.ps4_ftp, "download_media", return_value=("clip.mp4", b"video")) as download,
                patch.object(main.jobs, "create", return_value=job) as create,
                patch.object(main, "_build_animated_preview", return_value=expected) as preview,
            ):
                result = self.invoke("video", "animated", "/user/clip.mp4")

        self.assertEqual(result, expected)
        create.assert_called_once_with("animated", "clip.mp4", b"video")
        preview.assert_called_once()
        download.assert_called_once()


if __name__ == "__main__":
    unittest.main()
