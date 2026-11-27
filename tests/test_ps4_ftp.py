"""Tests for safe, read-only PS4 FTP browsing validation."""
import unittest
from unittest.mock import patch

from app import ps4_ftp


class Ps4FtpValidationTests(unittest.TestCase):
    def test_accepts_private_ipv4_and_normalizes_folder(self):
        self.assertEqual(
            ps4_ftp.validate_target("192.168.1.23", 2121, "/user/data/"),
            ("192.168.1.23", 2121, "/user/data"),
        )

    def test_rejects_public_ip_and_wrong_port(self):
        with self.assertRaises(ValueError):
            ps4_ftp.validate_target("8.8.8.8", 2121, "/")
        with self.assertRaises(ValueError):
            ps4_ftp.validate_target("192.168.1.23", 21, "/")

    def test_rejects_parent_path(self):
        with self.assertRaises(ValueError):
            ps4_ftp.validate_target("192.168.1.23", 2121, "/user/../system")


    def test_download_rejects_unsupported_extension_before_connecting(self):
        with patch("app.ps4_ftp.ftplib.FTP") as ftp:
            with self.assertRaises(ValueError):
                ps4_ftp.download_media("192.168.1.23", 2121, "/user/data/archive.zip")
            ftp.assert_not_called()

    def test_download_enforces_size_limit(self):
        class FakeFtp:
            def connect(self, *args, **kwargs): pass
            def login(self): pass
            def retrbinary(self, command, callback, blocksize=8192):
                callback(b"12345")
            def quit(self): pass

        with patch("app.ps4_ftp.ftplib.FTP", return_value=FakeFtp()):
            with self.assertRaisesRegex(ValueError, "512 MB"):
                ps4_ftp.download_media("192.168.1.23", 2121, "/user/data/photo.png", max_bytes=4)

    def test_download_returns_only_whitelisted_media(self):
        class FakeFtp:
            def connect(self, *args, **kwargs): pass
            def login(self): pass
            def retrbinary(self, command, callback, blocksize=8192):
                self.command = command
                callback(b"image-bytes")
            def quit(self): pass

        fake = FakeFtp()
        with patch("app.ps4_ftp.ftplib.FTP", return_value=fake):
            name, data = ps4_ftp.download_media("192.168.1.23", 2121, "/user/data/photo.png", max_bytes=100)
        self.assertEqual(name, "photo.png")
        self.assertEqual(data, b"image-bytes")
        self.assertEqual(fake.command, "RETR /user/data/photo.png")


    def test_rejects_loopback_link_local_and_ipv6(self):
        for host in ("127.0.0.1", "169.254.1.2", "::1"):
            with self.subTest(host=host), self.assertRaises(ValueError):
                ps4_ftp.validate_target(host, 2121, "/")

    def test_rejects_control_characters_in_path(self):
        for path in ("/user/data\r\nRETR /system/etc/passwd", "/user/\x00image.png", "/user/\x7f"):
            with self.subTest(path=repr(path)), self.assertRaises(ValueError):
                ps4_ftp.validate_target("192.168.1.23", 2121, path)

    def test_rejects_empty_or_directory_download(self):
        with patch("app.ps4_ftp.ftplib.FTP") as ftp:
            for path in ("/", "/user/data/"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    ps4_ftp.download_media("192.168.1.23", 2121, path)
            ftp.assert_not_called()

    def test_download_accepts_file_exactly_at_size_limit(self):
        class FakeFtp:
            def connect(self, *args, **kwargs): pass
            def login(self): pass
            def retrbinary(self, command, callback, blocksize=8192):
                callback(b"1234")
            def quit(self): pass

        with patch("app.ps4_ftp.ftplib.FTP", return_value=FakeFtp()):
            name, data = ps4_ftp.download_media(
                "192.168.1.23", 2121, "/user/data/photo.png", max_bytes=4
            )
        self.assertEqual(name, "photo.png")
        self.assertEqual(data, b"1234")

    def test_download_rejects_empty_remote_file(self):
        class FakeFtp:
            def connect(self, *args, **kwargs): pass
            def login(self): pass
            def retrbinary(self, command, callback, blocksize=8192): pass
            def quit(self): pass

        with patch("app.ps4_ftp.ftplib.FTP", return_value=FakeFtp()):
            with self.assertRaisesRegex(ValueError, "empty"):
                ps4_ftp.download_media("192.168.1.23", 2121, "/user/data/empty.png")


if __name__ == "__main__":
    unittest.main()
