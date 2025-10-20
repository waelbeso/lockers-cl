"""Utility helpers for interacting with the locker hardware."""

from __future__ import annotations

from pathlib import Path
import logging
from typing import Mapping

LOGGER = logging.getLogger(__name__)

# Serial connection defaults. These mirror the previously in-lined constants.
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 9600
SERIAL_BYTESIZE = 8
SERIAL_STOPBITS = 1
SERIAL_PARITY = "N"
SERIAL_TIMEOUT = 10

# Byte commands used by the locker controller for the three available boxes.
LOCKER_COMMANDS: Mapping[str, tuple[int, ...]] = {
    "1": (0x7A, 0x01, 0x01, 0x33, 0x49),
    "2": (0x7A, 0x01, 0x02, 0x33, 0x4A),
    "3": (0x7A, 0x01, 0x03, 0x33, 0x4B),
}

# Mapping between the cell identifiers stored in the database and the physical
# locker numbers that the controller expects.
CELL_TO_LOCKER: Mapping[str, str] = {
    "89E154gs12828": "1",
    "34r0361R8t765": "2",
    "416d61g56D509": "3",
}


def _serial_module():  # pragma: no cover - exercised indirectly in tests
    """Return the serial module if it is available.

    Importing :mod:`serial` at module import time makes the application fail
    early when the dependency or the underlying hardware is missing. Delaying
    the import keeps the web interface usable in development and allows the
    functions to communicate errors gracefully.
    """

    try:
        import serial  # type: ignore
    except ImportError:  # pragma: no cover - depends on environment
        return None
    return serial


def trigger_locker(locker_identifier: str) -> bool:
    """Send the open command to the configured locker.

    Parameters
    ----------
    locker_identifier:
        The logical locker number (``"1"`` – ``"3"``).

    Returns
    -------
    bool
        ``True`` when the command was dispatched successfully. ``False`` when
        the locker identifier is unknown, the serial module is unavailable or a
        communication error occurred.
    """

    command = LOCKER_COMMANDS.get(locker_identifier)
    if command is None:
        LOGGER.warning("Unknown locker identifier: %s", locker_identifier)
        return False

    serial = _serial_module()
    if serial is None:
        LOGGER.error("pyserial is not installed; cannot trigger locker %s", locker_identifier)
        return False

    SerialException = getattr(serial, "SerialException", Exception)

    try:
        with serial.Serial(  # type: ignore[attr-defined]
            SERIAL_PORT,
            SERIAL_BAUDRATE,
            bytesize=SERIAL_BYTESIZE,
            stopbits=SERIAL_STOPBITS,
            parity=SERIAL_PARITY,
            timeout=SERIAL_TIMEOUT,
        ) as connection:
            connection.write(bytes(command))
            connection.read()
    except SerialException:  # pragma: no cover - exercised via mocks
        LOGGER.exception("Failed to open locker %s", locker_identifier)
        return False

    return True


def remove_qr_code_file(static_root: str | Path, cell_key: str) -> bool:
    """Remove the QR code image generated for the provided ``cell_key``.

    Parameters
    ----------
    static_root:
        Base directory that stores generated QR code images.
    cell_key:
        The access code associated with the QR code image.

    Returns
    -------
    bool
        ``True`` when the file existed and was removed successfully; ``False``
        when the file did not exist or removing it failed for any reason.
    """

    image_path = Path(static_root) / f"{cell_key}.png"
    try:
        image_path.unlink()
    except FileNotFoundError:
        LOGGER.debug("QR code image %s did not exist", image_path)
        return False
    except OSError:  # pragma: no cover - depends on filesystem permissions
        LOGGER.exception("Unable to remove QR code image %s", image_path)
        return False
    return True


def locker_for_cell(cell_identifier: str) -> str | None:
    """Translate a cell identifier to the physical locker number."""

    return CELL_TO_LOCKER.get(cell_identifier)

