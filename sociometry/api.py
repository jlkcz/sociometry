# -*- coding: utf8 -*-
from __future__ import print_function, generators
import json
from flask import Flask, url_for, render_template, request, g, flash, redirect, jsonify
from sociometry import app, models as m, g

#@app.route("/api/child/<int:childid>")
#def api_child(childid):
#    child = g.curr.execute("SELECT * FROM children WHERE id=? ORDER BY name", [childid]).fetchone()
#    if child is None:
#        return jsonify([])
#    else:
#        return jsonify(child)
#
#
#@app.route("/api/friendship_ids/<int:childid>")
#def api_friendship_ids(childid):
#    friendships = g.curr.execute('SELECT likes FROM friendships WHERE who=?', [childid]).fetchall()
#    if friendships is None:
#        return jsonify([])
#    result = {"likes": [elem["likes"] for elem in friendships]}
#    return jsonify(result)
#
#
#@app.route("/api/children_in_class/<int:classid>")
#def api_children_in_class(classid):
#    ids = g.curr.execute("SELECT id FROM children WHERE class=?", [classid]).fetchall()
#    print(ids)
#    return jsonify({"ids": [id["id"] for id in ids]})
#
#@app.route("/api/save", methods=["GET", "POST"])
#def api_save():
#    result = {"returncode": 1}
#    g.db.execute('BEGIN TRANSACTION;')
#    print(request.form["childid"])
#    child_class = g.curr.execute("SELECT class FROM children WHERE id=?", request.form["childid"]).fetchone()["class"]
#
#    if child_class is None:
#        #child doesn't exist
#        result["returncode"] = 0
#        result["reason"] = "No such child"
#        return jsonify(result)
#
#    g.curr.execute("DELETE FROM friendships WHERE who=?", request.form["childid"])
#
#    #No friends :-(
#    if request.form["friends"] is None:
#            g.db.commit()
#            return jsonify(result)
#
#    friendships_data = request.values.getlist('friends')
#    friendships_list = [(child_class, int(request.form["childid"]), int(likes)) for likes in friendships_data]
#    g.curr.executemany("INSERT INTO friendships (class, who, likes) VALUES (?,?,?)", friendships_list)
#    g.db.commit()
#    return jsonify(result)

@app.route("/api/edit/class/<int:classid>", methods=["POST"])
def api_edit_class(classid):
    m.ClassModel.rename(classid, request.form["name"])
    return jsonify([])

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