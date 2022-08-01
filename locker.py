

#ln -s /usr/lib/python3/dist-packages/gi/ lib/python3.8/site-packages/

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import  Gio, Gtk, Gdk
#from gi.repository import  GLib
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

import threading
import time

import sys
import os
from django.core.wsgi import get_wsgi_application
from django.core.management.commands import runserver

import sys
sys.modules["gi.overrides.Gst"] = None
sys.modules["gi.overrides.GstPbutils"] = None


PORT = 8000
IP = '127.0.0.1'
ROOT_URL = f'http://{IP}:{PORT}'

class Window(Gtk.ApplicationWindow):

    def __init__(self, app):
        super(Window, self).__init__(title="Application", application=app)

        self.set_default_size(800, 600)

        webView = WebKit2.WebView()
        self.webView = webView
        self.add(webView)

        webView.load_uri(ROOT_URL) # Here it works on main thread


    def quitApp(self, par):
        app.quit()



class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="com.github.waelbeso.lockers-cl",
            #flags= Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
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




    def start_django(self):
        self.django.run(port=PORT,addr=IP ,wsgi_handler=get_wsgi_application())
        #GLib.idle_add(self.django.run(port=PORT,addr=IP ,wsgi_handler=get_wsgi_application()) , self.event)
        #self.event.wait()
        #thread.daemon = True
        #thread.start()
        #time.sleep(1)
        return 0

def provide_GUI_for(application):
    app = Application()
    app.django = application
    thread        = threading.Thread(name = "Django", target=app.start_django)
    app.event     = threading.Event()
    thread.daemon = True
    thread.start()
    app.run(sys.argv)

    
    return 0

def main(argv=None):

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cl.settings')
    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    app = runserver
    sys.exit(provide_GUI_for(app))

if __name__ == '__main__':
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cl.settings')
    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    app = runserver
    sys.exit(provide_GUI_for(app))

    #app = Application()
    #app.run(sys.argv)
