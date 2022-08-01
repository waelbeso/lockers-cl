import sys
import os
from django.core.wsgi import get_wsgi_application
import sys

from PyQt5.QtCore import QThread, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage
from PyQt5.QtWidgets import QApplication

from django.core.management.commands import runserver
PORT = 8000
IP = '127.0.0.1'
ROOT_URL = f'http://{IP}:{PORT}'

class Thread(QThread):
    def __init__(self, application):
        QThread.__init__(self)
        self.application = application
    def __del__(self):
        self.wait()
    def run(self):
        self.application.run(port=PORT,addr=IP ,wsgi_handler=get_wsgi_application())

def provide_GUI_for(application):
    qtapp = QApplication(sys.argv)

    webapp = Thread(application)
    webapp.start()

    qtapp.aboutToQuit.connect(webapp.terminate)

    webview = QWebView()
    webview.load(QUrl(ROOT_URL))

    webview.show()
    webview.reload()
    return qtapp.exec_()




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




