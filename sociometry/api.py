# -*- coding: utf8 -*-
from __future__ import print_function, generators
import json
from flask import request, jsonify
from sociometry import app, models as m
import tempfile
import cairosvg

@app.route("/api/diagram/<int:classid>/<type>")
def api_diagram_data(classid, type):
    diagram_data = m.QuestionnaireModel.getDiagramData(classid, type)
    links_data = m.QuestionnaireModel.getLinksData(classid, type)
    diagram_data.update(links_data)
    return jsonify(diagram_data)

@app.route("/api/save/graph/<int:classid>/<type>", methods=["GET", "POST"])
def api_save_graph(classid, type):
    acquired_data = json.loads(request.data)
    m.DiagramModel.saveDiagram(classid, type, json.dumps(acquired_data))
    return "True"

@app.route("/api/get/graph/last/<int:classid>/<type>", methods=["GET", "POST"])
def api_get_last_graph(classid, type):
    line = m.DiagramModel.getLastDiagram(classid, type)
    return jsonify(json.loads(line["data"]))

@app.route("/api/svg/to/png", methods=["POST"])
def api_svg_to_png():
    with tempfile.TemporaryFile(suffix=".png", prefix="tmp") as out:
        cairosvg.svg2png(bytestring=request.form["pcontent"], write_to=out)
        out.seek(0)
        key = m.TempfileModel.store_file(request.form["filename"], buffer(out.read()))
        return jsonify({"name": key})
