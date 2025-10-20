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
    @mock.patch("lockers.subprocess.Popen")
    def test_run_server_starts_django(self, popen):
        config = lockers.DesktopConfig(host="localhost", port=8081)
        fake_process = mock.Mock()
        fake_process.wait.return_value = 0
        fake_process.poll.return_value = 0
        popen.return_value = fake_process

        captured: list[object] = []

        with mock.patch.dict(os.environ, {}, clear=True):
            lockers._run_server(config, on_process=captured.append)

        popen.assert_called_once()
        command = popen.call_args.args[0]
        self.assertEqual(
            command,
            [
                sys.executable,
                "-m",
                "django",
                "runserver",
                "localhost:8081",
                "--noreload",
            ],
        )
        env = popen.call_args.kwargs["env"]
        self.assertIsInstance(env, dict)
        self.assertEqual(env["DJANGO_SETTINGS_MODULE"], "cl.settings")
        self.assertEqual(os.environ["DJANGO_SETTINGS_MODULE"], "cl.settings")
        self.assertEqual(captured, [fake_process])
        fake_process.wait.assert_called_once()
        fake_process.terminate.assert_not_called()

    def test_custom_start_url_is_used(self):
        config = lockers.DesktopConfig(start_url="http://example.test/app")
        self.assertEqual(config.root_url, "http://example.test/app")


class DesktopAppTests(unittest.TestCase):
    @mock.patch("lockers._load_gi_modules")
    @mock.patch("lockers._run_server")
    @mock.patch("lockers._run_gui")
    def test_start_creates_threads(self, run_gui, run_server, load_modules):
        run_gui.side_effect = lambda *args, **kwargs: None
        def fake_run_server(config, *, on_process=None):
            if on_process is not None:
                on_process(mock.Mock())

        run_server.side_effect = fake_run_server
        load_modules.return_value = object()

        app = lockers.DesktopApp(lockers.DesktopConfig())
        app.start()

        self.assertIsNotNone(app.gui_thread)
        self.assertIsNotNone(app.server_thread)
        self.assertIsNotNone(app.server_process)

        app.join()
        self.assertTrue(run_gui.called)
        self.assertTrue(run_server.called)
        load_modules.assert_called_once()

    @mock.patch("lockers.webbrowser.open", return_value=True)
    @mock.patch("lockers._load_gi_modules", side_effect=lockers.DesktopDependencyError("missing"))
    @mock.patch("lockers._run_server")
    def test_start_falls_back_to_browser(self, run_server, load_modules, browser_open):
        def fake_run_server(config, *, on_process=None):
            if on_process is not None:
                on_process(mock.Mock())

        run_server.side_effect = fake_run_server

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
        def fake_run_server(config, *, on_process=None):
            if on_process is not None:
                on_process(mock.Mock())

        run_server.side_effect = fake_run_server
        headless_gui.side_effect = lambda *args, **kwargs: None

        with mock.patch.dict(os.environ, {"LOCKERS_HEADLESS": "1"}):
            app = lockers.DesktopApp(lockers.DesktopConfig())
            app.start()
            app.join()

        headless_gui.assert_called_once()

    @mock.patch("lockers._terminate_process")
    def test_stop_terminates_running_server(self, terminate_process):
        app = lockers.DesktopApp()
        fake_process = mock.Mock()
        app.server_process = fake_process

        app.stop()

        terminate_process.assert_called_once_with(fake_process)
        self.assertIsNone(app.server_process)

    @mock.patch("lockers._terminate_process")
    def test_stop_handles_missing_process(self, terminate_process):
        app = lockers.DesktopApp()
        app.stop()
        terminate_process.assert_not_called()


if __name__ == "__main__":  # pragma: no cover - manual execution guard
    unittest.main()
