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


if __name__ == "__main__":
    unittest.main()
