import threading
import time
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2


from gi.repository import GLib
GLib.threads_init()

import sys
import os
from django.core.wsgi import get_wsgi_application
from django.core.management.commands import runserver


PORT = 8090
IP = '0.0.0.0'
ROOT_URL = f'http://{IP}:{PORT}'
 
def app_main():
    win = Gtk.Window(default_height=800, default_width=600)
    win.connect("destroy", Gtk.main_quit)

    webView = WebKit2.WebView()
    win.add(webView)

    webView.load_uri(ROOT_URL) # Here it works on main thread

    def start_django():
        django = runserver
        GLib.idle_add(django.run(port=PORT,addr=bytearray(IP,"ascii"),wsgi_handler=get_wsgi_application()) )


    win.show_all()
    thread = threading.Thread(name = "Django", target=start_django)
    thread.daemon = True
    thread.start()



def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cl.settings')
    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc    
    app_main()
    Gtk.main()
    
if __name__ == "__main__":
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
    app_main()
    Gtk.main()
