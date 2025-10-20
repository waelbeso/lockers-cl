from __future__ import annotations

import contextlib
import tempfile
from pathlib import Path
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

        @contextlib.contextmanager
        def dummy_factory(*args, **kwargs):
            class DummyConnection:
                def write(self, data: bytes):
                    calls["write"] = data

                def read(self, size: int = 1):  # pragma: no cover - nothing to return
                    return b""

            yield DummyConnection()

        locker.configure_serial_backend(dummy_factory)
        try:
            self.assertTrue(locker.trigger_locker("1"))
            self.assertEqual(calls["write"], bytes(locker.LOCKER_COMMANDS["1"]))
        finally:
            locker.configure_serial_backend(None)

    def test_trigger_locker_unknown_identifier(self):
        self.assertFalse(locker.trigger_locker("unknown"))


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    unittest.main()
