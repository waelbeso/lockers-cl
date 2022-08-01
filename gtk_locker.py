
#ln -s /usr/lib/python3/dist-packages/gi/ lib/python3.8/site-packages/

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import  GLib, Gio, Gtk, Gdk

gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

import threading
import time

import sys
import os
from django.core.wsgi import get_wsgi_application
from django.core.management.commands import runserver




PORT = 8000
IP = '127.0.0.1'
ROOT_URL = f'http://{IP}:{PORT}'

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super(Window, self).__init__(title="Application", application=app)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)
        self.set_default_size(800, 600)


        button = Gtk.Button.new_with_label("Click Me")
        button.connect("clicked", self.on_click_me_clicked)
        hbox.pack_start(button, True, True, 0)


    def quitApp(self, par):
        app.quit()

    def on_click_me_clicked(self, button):
        print('"Click me" button was clicked')

class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="com.github.waelbeso.lockers-cl",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )

        self.window = None

    def do_activate(self):
    
        self.win = Window(self)
        self.win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)


    def on_quit(self, action, param):
        self.quit()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0







def main(argv=None):
    app = Application()
    app.run(sys.argv)

if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)

