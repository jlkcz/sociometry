#!venv/bin/python
# -*- coding: utf8 -*-

from os import environ
from sociometry import app


class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    HOST = '127.0.0.1'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    HOST = "127.0.0.1"
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True

if "SM_PROD" in environ and environ["SM_PROD"] == '1':
    app.config.from_object(ProductionConfig())
else:
    app.config.from_object(DevelopmentConfig())


if "SM_HOST" in environ:
    app.config["host"] = environ["SM_HOST"]

app.run()
