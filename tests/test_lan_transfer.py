"""Regression tests for optional LAN transfer access boundaries."""
from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import main


class LanTransferBoundaryTests(unittest.TestCase):
    def request(self, host: str, path: str):
        return SimpleNamespace(
            client=SimpleNamespace(host=host),
            url=SimpleNamespace(path=path),
        )

    def test_remote_clients_are_blocked_when_lan_mode_is_off(self):
        async def downstream(_request):
            return "reached"

        with patch.object(main, "LAN_TRANSFER_TOKEN", ""):
            response = asyncio.run(
                main.restrict_lan_clients(self.request("192.168.1.20", "/api/system"), downstream)
            )
        self.assertEqual(response.status_code, 403)

    def test_remote_clients_can_only_reach_token_scoped_transfer_path(self):
        async def downstream(_request):
            return "reached"

        with patch.object(main, "LAN_TRANSFER_TOKEN", "test-secret"):
            allowed = asyncio.run(
                main.restrict_lan_clients(
                    self.request("192.168.1.20", "/transfer/test-secret/abc123"),
                    downstream,
                )
            )
            denied = asyncio.run(
                main.restrict_lan_clients(
                    self.request("192.168.1.20", "/api/workspace"),
                    downstream,
                )
            )
        self.assertEqual(allowed, "reached")
        self.assertEqual(denied.status_code, 403)

    def test_loopback_clients_keep_normal_editor_access(self):
        async def downstream(_request):
            return "reached"

        with patch.object(main, "LAN_TRANSFER_TOKEN", "test-secret"):
            response = asyncio.run(
                main.restrict_lan_clients(self.request("127.0.0.1", "/api/system"), downstream)
            )
        self.assertEqual(response, "reached")


if __name__ == "__main__":
    unittest.main()
