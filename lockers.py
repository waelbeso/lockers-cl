"""Utilities for launching the Smart Lockers desktop application."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import webbrowser
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Callable, Optional, Tuple

LOGGER = logging.getLogger(__name__)


class DesktopDependencyError(RuntimeError):
    """Raised when a runtime dependency required by the desktop UI is missing."""


@dataclass(frozen=True)
class DesktopConfig:
    """Configuration container used to launch the desktop application."""

    host: str = "0.0.0.0"
    port: int = 8090
    window_height: int = 800
    window_width: int = 600
    start_url: Optional[str] = None

    @property
    def root_url(self) -> str:
        """Return the URL loaded by the embedded WebKit view."""

        return self.start_url or f"http://{self.host}:{self.port}"


def _load_gi_modules() -> SimpleNamespace:
    """Import and configure the required PyGObject modules.

    Returns
    -------
    types.SimpleNamespace
        Namespace exposing the imported modules as attributes.

    Raises
    ------
    DesktopDependencyError
        If PyGObject or one of the requested libraries cannot be imported.
    """

    try:
        import gi
    except ImportError as exc:  # pragma: no cover - depends on system packages
        raise DesktopDependencyError(
            "PyGObject is required to launch the desktop interface."
        ) from exc

    gi.require_version("Gtk", "3.0")
    gi.require_version("WebKit2", "4.0")

    from gi.repository import GObject, GLib, Gtk, WebKit2  # type: ignore

    return SimpleNamespace(gi=gi, GObject=GObject, GLib=GLib, Gtk=Gtk, WebKit2=WebKit2)


def _initialise_threads(modules: SimpleNamespace) -> None:
    """Initialise GObject threading if the helper is available."""

    threads_init = getattr(modules.GObject, "threads_init", None)
    if callable(threads_init):  # pragma: no branch - simple attribute check
        threads_init()


def _run_gui(
    config: DesktopConfig,
    modules: Optional[SimpleNamespace] = None,
    ready_event: Optional[threading.Event] = None,
) -> None:
    """Launch the GTK application hosting the lockers web interface."""

    modules = modules or _load_gi_modules()
    _initialise_threads(modules)

    try:
        window = modules.Gtk.Window(
            default_height=config.window_height, default_width=config.window_width
        )
        window.connect("destroy", modules.Gtk.main_quit)

        web_view = modules.WebKit2.WebView()
        window.add(web_view)
        web_view.load_uri(config.root_url)
        window.show_all()

        if ready_event is not None:
            ready_event.set()

        LOGGER.info("Starting GTK main loop for lockers desktop UI")
        modules.Gtk.main()
    finally:
        if ready_event is not None:
            ready_event.set()


def _launch_system_browser(
    config: DesktopConfig,
    ready_event: Optional[threading.Event] = None,
) -> None:
    """Open the lockers interface in the user's default browser."""

    try:
        success = webbrowser.open(config.root_url, new=1)
        if not success:  # pragma: no cover - webbrowser returns False rarely
            raise DesktopDependencyError(
                "Unable to open the system web browser automatically."
            )
        LOGGER.info("Opened system browser for lockers interface at %s", config.root_url)
    finally:
        if ready_event is not None:
            ready_event.set()


def _headless_gui(
    config: DesktopConfig,
    ready_event: Optional[threading.Event] = None,
) -> None:
    """Skip GUI launch entirely when running in CI/headless environments."""

    LOGGER.info(
        "Headless mode enabled; skipping GUI/browser launch and waiting for server thread."
    )
    if ready_event is not None:
        ready_event.set()


def _headless_requested() -> bool:
    return os.environ.get("LOCKERS_HEADLESS", "").lower() in {"1", "true", "yes"}


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    """Attempt to terminate a subprocess gracefully, forcing if required."""

    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def _run_server(
    config: DesktopConfig, *, on_process: Optional[Callable[[subprocess.Popen[bytes]], None]] = None
) -> None:
    """Run Django's development server inside a worker thread."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cl.settings")

    command = [
        sys.executable,
        "-m",
        "django",
        "runserver",
        f"{config.host}:{config.port}",
        "--noreload",
    ]
    env = os.environ.copy()

    LOGGER.info("Starting Django development server on %s:%s", config.host, config.port)

    try:
        process = subprocess.Popen(command, env=env)
    except FileNotFoundError as exc:  # pragma: no cover - depends on interpreter availability
        raise DesktopDependencyError("Python is required to launch the Django server.") from exc

    if on_process is not None:
        on_process(process)

    try:
        process.wait()
    except KeyboardInterrupt:  # pragma: no cover - defensive guard
        LOGGER.info("Server thread received interrupt; terminating Django process")
    finally:
        _terminate_process(process)


class DesktopApp:
    """Coordinator that starts both the Django server and the GTK interface."""

    def __init__(self, config: Optional[DesktopConfig] = None) -> None:
        self.config = config or DesktopConfig()
        self.gui_thread: Optional[threading.Thread] = None
        self.server_thread: Optional[threading.Thread] = None
        self._ready_event: Optional[threading.Event] = None
        self.server_process: Optional[subprocess.Popen[bytes]] = None

    def start(self) -> "DesktopApp":
        """Start the desktop application threads."""

        self._ready_event = threading.Event()

        def _capture_process(process: subprocess.Popen[bytes]) -> None:
            self.server_process = process

        self.server_thread = threading.Thread(
            target=_run_server,
            args=(self.config,),
            kwargs={"on_process": _capture_process},
            name="LockerServer",
            daemon=True,
        )
        self.server_thread.start()

        gui_target: Callable[..., None]
        gui_args: Tuple[object, ...]
        gui_kwargs = {"ready_event": self._ready_event}

        if _headless_requested():
            gui_target = _headless_gui
            gui_args = (self.config,)
        else:
            try:
                modules = _load_gi_modules()
            except DesktopDependencyError as exc:  # pragma: no cover - depends on env
                LOGGER.warning(
                    "GTK/WebKit bindings are unavailable (%s); falling back to the system browser.",
                    exc,
                )
                gui_target = _launch_system_browser
                gui_args = (self.config,)
            else:
                gui_target = _run_gui
                gui_args = (self.config, modules)

        self.gui_thread = threading.Thread(
            target=gui_target,
            args=gui_args,
            kwargs=gui_kwargs,
            name="LockerGUI",
        )
        self.gui_thread.start()

        return self

    def wait_for_gui(self, timeout: Optional[float] = None) -> bool:
        """Block until the GUI thread signalled that the window is ready."""

        if self._ready_event is None:
            return False
        return self._ready_event.wait(timeout)

    def join(self) -> None:
        """Wait for the worker threads to finish."""

        if self.gui_thread is not None:
            self.gui_thread.join()
        if self.server_thread is not None:
            self.server_thread.join()

    def stop(self) -> None:
        """Terminate the managed Django server process if it is running."""

        if self.server_process is not None:
            _terminate_process(self.server_process)
            self.server_process = None


def main() -> None:
    """Console script entry point used by ``python -m lockers``."""

    logging.basicConfig(level=logging.INFO)
    app = DesktopApp().start()
    try:
        app.join()
    except KeyboardInterrupt:
        LOGGER.info("Received interrupt; shutting down desktop launcher")
        app.stop()
        app.join()


if __name__ == "__main__":  # pragma: no cover - manual execution hook
    main()
