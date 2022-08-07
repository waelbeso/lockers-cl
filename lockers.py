import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk



def main(argv=None):
 win = Gtk.Window()
 win.connect("destroy", Gtk.main_quit)
 win.show_all()
 Gtk.main()

if __name__ == "__main__":
 win = Gtk.Window()
 win.connect("destroy", Gtk.main_quit)
 win.show_all()
 Gtk.main()
