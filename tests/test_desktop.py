from __future__ import annotations

import os
import sys
import threading
import types
import unittest
from unittest import mock

import lockers


class DummyWindow:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.connected = []
        self.children = []
        self.shown = False

    def connect(self, signal, callback):
        self.connected.append((signal, callback))

    def add(self, child):
        self.children.append(child)

    def show_all(self):
        self.shown = True


class DummyWebView:
    def __init__(self):
        self.loaded_uri: str | None = None

    def load_uri(self, uri):
        self.loaded_uri = uri


class DesktopGuiTests(unittest.TestCase):
    def setUp(self):
        self.created_windows: list[DummyWindow] = []
        self.created_webviews: list[DummyWebView] = []

        class TrackingWindow(DummyWindow):
            def __init__(inner_self, **kwargs):
                super().__init__(**kwargs)
                self.created_windows.append(inner_self)

        class TrackingWebView(DummyWebView):
            def __init__(inner_self):
                super().__init__()
                self.created_webviews.append(inner_self)

        self.modules = types.SimpleNamespace(
            GObject=types.SimpleNamespace(threads_init=lambda: setattr(self, "threads", True)),
            Gtk=types.SimpleNamespace(
                Window=TrackingWindow,
                main=lambda: setattr(self, "gtk_main", True),
                main_quit=lambda *args: None,
            ),
            WebKit2=types.SimpleNamespace(WebView=TrackingWebView),
        )

    def test_run_gui_loads_expected_url(self):
        config = lockers.DesktopConfig(host="127.0.0.1", port=9000)
        ready_event = threading.Event()

        lockers._run_gui(config, modules=self.modules, ready_event=ready_event)

        self.assertTrue(getattr(self, "threads", False))
        self.assertTrue(getattr(self, "gtk_main", False))
        self.assertEqual(len(self.created_windows), 1)
        self.assertEqual(len(self.created_webviews), 1)
        window = self.created_windows[0]
        self.assertIn(("destroy", self.modules.Gtk.main_quit), window.connected)
        self.assertEqual(window.kwargs["default_height"], config.window_height)
        self.assertEqual(window.kwargs["default_width"], config.window_width)
        self.assertTrue(window.shown)
        self.assertIs(window.children[0], self.created_webviews[0])
        self.assertEqual(self.created_webviews[0].loaded_uri, "http://127.0.0.1:9000")
        self.assertTrue(ready_event.is_set())


class DesktopServerTests(unittest.TestCase):
    def test_run_server_starts_django(self):
        config = lockers.DesktopConfig(host="localhost", port=8081)
        fake_management = types.ModuleType("django.core.management")
        fake_management.call_command = mock.Mock()
        fake_core = types.ModuleType("django.core")
        fake_core.management = fake_management
        fake_django = types.ModuleType("django")
        fake_django.core = fake_core

        with mock.patch.dict(
            sys.modules,
            {
                "django": fake_django,
                "django.core": fake_core,
                "django.core.management": fake_management,
            },
        ):
            with mock.patch.dict(os.environ, {}, clear=True):
                lockers._run_server(config)
                fake_management.call_command.assert_called_once_with(
                    "runserver", "localhost:8081"
                )
                self.assertEqual(os.environ["DJANGO_SETTINGS_MODULE"], "cl.settings")

    def test_custom_start_url_is_used(self):
        config = lockers.DesktopConfig(start_url="http://example.test/app")
        self.assertEqual(config.root_url, "http://example.test/app")


class DesktopAppTests(unittest.TestCase):
    @mock.patch("lockers._load_gi_modules")
    @mock.patch("lockers._run_server")
    @mock.patch("lockers._run_gui")
    def test_start_creates_threads(self, run_gui, run_server, load_modules):
        run_gui.side_effect = lambda *args, **kwargs: None
        run_server.side_effect = lambda *args, **kwargs: None
        load_modules.return_value = object()

        app = lockers.DesktopApp(lockers.DesktopConfig())
        app.start()

        self.assertIsNotNone(app.gui_thread)
        self.assertIsNotNone(app.server_thread)

        app.join()
        self.assertTrue(run_gui.called)
        self.assertTrue(run_server.called)
        load_modules.assert_called_once()

    @mock.patch("lockers.webbrowser.open", return_value=True)
    @mock.patch("lockers._load_gi_modules", side_effect=lockers.DesktopDependencyError("missing"))
    @mock.patch("lockers._run_server")
    def test_start_falls_back_to_browser(self, run_server, load_modules, browser_open):
        run_server.side_effect = lambda *args, **kwargs: None

        app = lockers.DesktopApp(lockers.DesktopConfig())
        app.start()

        self.assertIsNotNone(app.gui_thread)
        self.assertTrue(browser_open.called)

        app.join()
        load_modules.assert_called_once()
        browser_open.assert_called_once()

    def test_wait_for_gui_without_start_returns_false(self):
        app = lockers.DesktopApp()
        self.assertFalse(app.wait_for_gui(0.01))

    @mock.patch("lockers.webbrowser.open", return_value=False)
    def test_launch_system_browser_sets_event_on_failure(self, browser_open):
        event = threading.Event()
        with self.assertRaises(lockers.DesktopDependencyError):
            lockers._launch_system_browser(lockers.DesktopConfig(), ready_event=event)

        self.assertTrue(event.is_set())
        browser_open.assert_called_once()

    @mock.patch("lockers._headless_gui")
    @mock.patch("lockers._run_server")
    def test_headless_mode_skips_gui_launch(self, run_server, headless_gui):
        run_server.side_effect = lambda *args, **kwargs: None
        headless_gui.side_effect = lambda *args, **kwargs: None

        with mock.patch.dict(os.environ, {"LOCKERS_HEADLESS": "1"}):
            app = lockers.DesktopApp(lockers.DesktopConfig())
            app.start()
            app.join()

        headless_gui.assert_called_once()


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    unittest.main()
