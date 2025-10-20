#!/usr/bin/env python3
"""Automated smoke test used by CI to validate the kiosk workflow."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path

import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cl.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402

from web import locker, models  # noqa: E402


BASE_URL = "http://127.0.0.1:8090"


def wait_for_server(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=1.0)
        except requests.RequestException:
            time.sleep(0.5)
            continue
        if response.status_code < 500:
            return
        time.sleep(0.5)
    raise RuntimeError(f"Server at {url} did not respond in time")


def main() -> None:
    call_command("migrate", interactive=False)
    call_command("check")

    env = os.environ.copy()
    env.setdefault("LOCKERS_HEADLESS", "1")
    env.setdefault("LOCKERS_SERIAL_BACKEND", "mock")

    process = subprocess.Popen(["python", "lockers.py"], env=env)
    try:
        wait_for_server(BASE_URL)

        slug = next(iter(locker.CELL_TO_LOCKER))
        key_response = requests.get(f"{BASE_URL}/key/{slug}/", timeout=5)
        key_response.raise_for_status()

        latest_cell = models.Cell.objects.latest("id")
        qr_path = Path(settings.STATIC_ROOT) / f"{latest_cell.code}.png"
        if not qr_path.exists():
            raise RuntimeError(f"Expected QR image {qr_path} to exist")

        home_response = requests.post(
            BASE_URL + "/",
            data={"code": latest_cell.code},
            timeout=5,
        )
        home_response.raise_for_status()

        if qr_path.exists():
            raise RuntimeError("QR image was not removed after redemption")
        if models.Cell.objects.filter(code=latest_cell.code).exists():
            raise RuntimeError("Locker code was not cleared from the database")
    finally:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    main()
