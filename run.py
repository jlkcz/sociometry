#!venv/bin/python
# -*- coding: utf8 -*-

from sociometry import app
app.config["TRAP_HTTP_EXCEPTIONS"] = True
app.run(debug=True,host='0.0.0.0')
