#!venv/bin/python
# -*- coding: utf8 -*-
from sociometry import app
import os.path, sys
import subprocess
import time

DEBUG = True

class DevelopmentConfig(object):
    DEBUG = True
    TESTING = True
    HOST = "127.0.0.1"
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True

class ProductionConfig(object):
    DEBUG = False
    TESTING = False
    HOST = "127.0.0.1"
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False

def find_appdata():
    APPNAME = "sociometry"
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        appdata = os.path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
    elif sys.platform == 'win32':
        appdata = os.path.join(os.environ['APPDATA'], APPNAME)
    else:
        appdata = os.path.expanduser(os.path.join("~", "." + APPNAME))
    return appdata


def launch_browser():
    time.sleep(3)
    print("====launch_browser()====")
    address = "http://127.0.0.1:5000"
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', address))
    elif os.name == 'nt':
        os.startfile(address)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', address))

if DEBUG:
    app.config.from_object(DevelopmentConfig())
    app.config["DATABASE"] = "./sociometry.db"
else:
    app.config.from_object(ProductionConfig())
    app.config["DATABASE"] = find_appdata()+"/sociometry.db"

app.config["ALLOW_B3"] = True

if __name__ == "__main__":
    app.run()
    sys.exit(0)
