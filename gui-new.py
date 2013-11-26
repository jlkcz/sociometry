#!venv/bin/python
# -*- coding: utf8 -*-
from Tkinter import *
from ttk import *
import os, sys
import subprocess
import time
import signal

def launch_browser():
    address = "http://127.0.0.1:5000"
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', address))
    elif os.name == 'nt':
        os.startfile(address)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', address))

if __name__ == "__main__":
    server = subprocess.Popen(['./cli.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    main = Tk()
    running_str = StringVar()
    running_str.set("Off")
    startstop_str = StringVar()
    startstop_str.set("Zapnout")
    appname = Label(main, text="Sociometry v.0.0.1", anchor="center")
    appname.grid(row=0, column=0, columnspan=2, pady=2)
    #running_frame = LabelFrame(main, text="Je zapnuto?")
    #running_frame.grid(row=1, column=0)
    #running = Label(running_frame, textvariable=running_str, anchor="center")
    #running.grid(row=0, column=0, padx=10, pady=10)
    #toggleoff = Button(running_frame, textvariable=startstop_str, command=toggle_server)
    #toggleoff.grid(row=0, column=1,  padx=10, pady=10)
    browser = Button(main, text=u"Spustit v prohlížeči", command=launch_browser)
    browser.grid(row=2, column=0, columnspan=2)
    main.mainloop()
    server.send_signal(sig=signal.SIGINT)
    server.send_signal(sig=signal.SIGTERM)
    time.sleep(5)
    sys.exit(0)




