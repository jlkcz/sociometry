#!venv/bin/python
# -*- coding: utf8 -*-
from __future__ import print_function, generators
from flask import Flask, url_for, render_template, request, g, flash, redirect, jsonify
import datetime
import sqlite3
from sqlite3 import OperationalError

app = Flask("sociometry")
app.secret_key = 'jlkczisdabestwithverywrongsecretkey'
DATABASE = "sociometry.db"


#Databases
def connect_to_database():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    return conn


@app.before_request
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = connect_to_database()
        #g.cur is legacy and will be removed
        g.curr = g.db.cursor()
        g.cur = g.curr
        #Check if we have DB already created
        try:
            g.db.execute("SELECT * FROM children")
        except OperationalError:
            init_db()
    return db



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def redirect_url(url=None, **kwargs):
    if url is not None:
        return url_for(url, **kwargs)
    return request.args.get('next') or request.referrer or url_for("index")


def init_db():
    with app.open_resource('db.sql') as f:
            print("creating DB")
            g.db.cursor().executescript(f.read())
            g.db.commit()


#define Jinja2 filter datetime (SQLite has no reasonable way to work with dates)
def format_datetime(value):
    return datetime.datetime.fromtimestamp(int(value)).strftime("%H:%M %d.%m.%Y")
app.jinja_env.filters["datetime"] = format_datetime

import sociometry.views
import sociometry.api
import sociometry.models