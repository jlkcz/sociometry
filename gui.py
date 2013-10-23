#!venv/bin/python
# -*- coding: utf8 -*-
from Tkinter import *
from ttk import *
import multiprocessing
import os, sys
import subprocess
from sociometry import app

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
    address = "http://127.0.0.1:5000"
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', address))
    elif os.name == 'nt':
        os.startfile(address)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', address))

def make_ui(server):
    def terminate_server():
            if server is not None and server.is_alive():
                server.terminate()
                #server.join()
            main.destroy()

    def toggle_server():
        global server
        if server.is_alive():
            server.terminate()
            server.join()
            running_str.set("Off")
            startstop_str.set("Zapnout")
            main.update()
        else:
            if server.exitcode:
                server = multiprocessing.Process(target=run_in_behind, name="server")
            server.start()
            running_str.set("On")
            startstop_str.set("Vypnout")
            main.update()

    main = Tk()
    running_str = StringVar()
    running_str.set("Off")
    startstop_str = StringVar()
    startstop_str.set("Zapnout")
    appname = Label(main, text="Sociometry v.0.0.1", anchor="center")
    appname.grid(row=0, column=0, columnspan=2, pady=2)
    running_frame = LabelFrame(main, text="Je zapnuto?")
    running_frame.grid(row=1, column=0)
    running = Label(running_frame, textvariable=running_str, anchor="center")
    running.grid(row=0, column=0, padx=10, pady=10)
    toggleoff = Button(running_frame, textvariable=startstop_str, command=toggle_server)
    toggleoff.grid(row=0, column=1,  padx=10, pady=10)
    browser = Button(main, text=u"Spustit v prohlížeči", command=launch_browser)
    browser.grid(row=2, column=0, columnspan=2)
    main.protocol("WM_DELETE_WINDOW", terminate_server)
    main.mainloop()



def run_in_behind():
    config = {
        "DEBUG": False,
        "HOST": "127.0.0.1"
    }
    app.config.from_object(config)
    app.config["DATABASE"] = os.path.join(find_appdata(), "sociometry.db")
    app.run()

if __name__ == "__main__":
    server = multiprocessing.Process(target=run_in_behind, name="server")
    make_ui(server)
    print("All done, yabadabadoo!")
