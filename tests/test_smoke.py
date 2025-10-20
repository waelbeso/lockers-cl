"""End-to-end smoke tests that exercise the QR workflow without hardware."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cl.settings")

django = pytest.importorskip("django")
django.setup()

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from web import locker, models


class LockerWorkflowSmokeTest(TestCase):
    """Validate QR code generation and redemption via the Django test client."""

    @classmethod
    def setUpTestData(cls):  # type: ignore[override]
        call_command("migrate", verbosity=0)

    def setUp(self) -> None:
        super().setUp()
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        self.commands: list[bytes] = []

        @contextlib.contextmanager
        def fake_serial(*args, **kwargs):
            class DummyConnection:
                def write(self, data: bytes):
                    self.commands.append(data)

                def read(self, size: int = 1):
                    return b"\x06"  # ACK byte from the controller.

            yield DummyConnection()

        locker.configure_serial_backend(fake_serial)
        self.addCleanup(lambda: locker.configure_serial_backend(None))

        self.client = Client()

    def test_generate_and_consume_qr_code(self) -> None:
        slug = next(iter(locker.CELL_TO_LOCKER))

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        static_root = Path(self.tempdir.name)
        with self.settings(STATIC_ROOT=static_root):
            qr_response = self.client.get(reverse("key", args=[slug]))

            self.assertEqual(qr_response.status_code, 200)
            self.assertIn("cell_key", qr_response.context)

            code_value = qr_response.context["cell_key"]
            qr_file = static_root / f"{code_value}.png"
            self.assertTrue(qr_file.exists(), "QR image should be written to STATIC_ROOT")
            self.assertTrue(models.Cell.objects.filter(code=code_value).exists())

            unlock_response = self.client.post(reverse("home"), {"code": code_value})
            self.assertEqual(unlock_response.status_code, 200)

        self.assertFalse(qr_file.exists(), "QR image should be removed after redemption")
        self.assertFalse(models.Cell.objects.filter(code=code_value).exists())
        self.assertEqual(
            self.commands,
            [bytes(locker.LOCKER_COMMANDS[locker.CELL_TO_LOCKER[slug]])],
        )
