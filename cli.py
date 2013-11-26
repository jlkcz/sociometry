#!venv/bin/python
# -*- coding: utf8 -*-

from sociometry import app

class DevelopmentConfig(object):
    DEBUG = True
    TESTING = True
    HOST = "127.0.0.1"
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True

app.config.from_object(DevelopmentConfig())
app.config["DATABASE"] = "./sociometry.db"
app.config["ALLOW_B3"] = False
app.run()