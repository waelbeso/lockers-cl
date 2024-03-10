
import threading
import gi

#https://stackoverflow.com/questions/35700140/pygtk-run-gtk-main-loop-in-a-seperate-thread
#https://www.programcreek.com/python/example/88995/gi.repository.GLib.threads_init

# Event marking the GUI thread as having imported GTK.  GTK must not
# be imported before this event's flag is set.
gui_ready = threading.Event()

PORT = 8090
IP = '0.0.0.0'
ROOT_URL = f'http://{IP}:{PORT}'

def run_gui_thread():
    from gi.repository import GObject as gobject
    gobject.threads_init()
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk as gtk
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2
    gui_ready.set()
    win = gtk.Window(default_height=800, default_width=600)
    win.connect("destroy", gtk.main_quit)
    webView = WebKit2.WebView()
    win.add(webView)
    webView.load_uri(ROOT_URL) 
    win.show_all()
    gtk.main()

gui_thread = threading.Thread(target=run_gui_thread)
gui_thread.start()


# wait for the GUI thread to initialize GTK
gui_ready.wait()

# it is now safe to import GTK-related stuff
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2

import sys
import os
from django.core.wsgi import get_wsgi_application
from django.core.management.commands import runserver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cl.settings')
try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
        ) from exc  


def start_django():
    django = runserver
    #logging.info('D-Bus process started')
    from gi.repository import GLib
    GLib.idle_add(django.run(port=PORT,addr=bytearray(IP,"ascii"),wsgi_handler=get_wsgi_application()) )

worker = threading.Thread(name = "Django", target=start_django)
print ('starting Django work...')
worker.start()


    
if __name__ == "__main__": 
    print("start __main__ ......")

def main():
    print("start main()......")






"""import threading
gui_ready = threading.Event()

import time
import gi
from gi.repository import GLib



if getattr(GLib, "threads_init", None) is not None:
    GLib.threads_init()

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2



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
        #logging.info('D-Bus process started')
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
    #Run administrative tasks.
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

"""