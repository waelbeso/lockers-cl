from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

from web import locker


class LockerHelpersTests(unittest.TestCase):
    def test_remove_qr_code_file_handles_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            code = "123456"
            image_path = Path(tmp_dir) / f"{code}.png"
            image_path.write_text("test")

            self.assertTrue(locker.remove_qr_code_file(tmp_dir, code))
            self.assertFalse(image_path.exists())
            # Subsequent removals quietly report the missing file.
            self.assertFalse(locker.remove_qr_code_file(tmp_dir, code))

    def test_trigger_locker_success_with_mock_serial(self):
        calls: dict[str, bytes] = {}

        class DummySerial:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def write(self, data: bytes):
                calls["write"] = data

            def read(self):  # pragma: no cover - nothing to return
                return b""

        dummy_serial = SimpleNamespace(Serial=DummySerial, SerialException=Exception)

        original_serial_module = locker._serial_module
        try:
            locker._serial_module = lambda: dummy_serial
            self.assertTrue(locker.trigger_locker("1"))
            self.assertEqual(calls["write"], bytes(locker.LOCKER_COMMANDS["1"]))
        finally:
            locker._serial_module = original_serial_module

    def test_trigger_locker_unknown_identifier(self):
        self.assertFalse(locker.trigger_locker("unknown"))


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    unittest.main()
