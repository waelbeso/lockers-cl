"""Utilities for launching the Smart Lockers desktop application."""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional

LOGGER = logging.getLogger(__name__)

    return SimpleNamespace(gi=gi, GObject=GObject, GLib=GLib, Gtk=Gtk, WebKit2=WebKit2)

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

    try:
        window = modules.Gtk.Window(
            default_height=config.window_height, default_width=config.window_width
        )
        window.connect("destroy", modules.Gtk.main_quit)

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

        if ready_event is not None:
            ready_event.set()

def _run_server(config: DesktopConfig) -> None:
    """Run Django's development server inside a worker thread."""

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cl.settings")
    try:
        from django.core.management import call_command
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise DesktopDependencyError("Django must be installed to run the desktop UI.") from exc

    LOGGER.info("Starting Django development server on %s:%s", config.host, config.port)
    call_command("runserver", f"{config.host}:{config.port}")

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

class DesktopApp:
    """Coordinator that starts both the Django server and the GTK interface."""

    def __init__(self, config: Optional[DesktopConfig] = None) -> None:
        self.config = config or DesktopConfig()
        self.gui_thread: Optional[threading.Thread] = None
        self.server_thread: Optional[threading.Thread] = None
        self._ready_event: Optional[threading.Event] = None

    def start(self) -> "DesktopApp":
        """Start the desktop application threads."""

        self._ready_event = threading.Event()

        self.server_thread = threading.Thread(
            target=_run_server,
            args=(self.config,),
            name="LockerServer",
        )
        self.server_thread.start()

        self.gui_thread = threading.Thread(
            target=_run_gui,
            args=(self.config, None, self._ready_event),
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

def main() -> None:
    """Console script entry point used by ``python -m lockers``."""

    logging.basicConfig(level=logging.INFO)
    DesktopApp().start().join()

    def wait_for_gui(self, timeout: Optional[float] = None) -> bool:
        """Block until the GUI thread signalled that the window is ready."""

if __name__ == "__main__":  # pragma: no cover - manual execution hook
    main()
