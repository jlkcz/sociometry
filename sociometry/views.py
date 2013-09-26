# -*- coding: utf8 -*-
from __future__ import print_function, generators
from flask import url_for, render_template, request, g, flash, redirect, abort
from sociometry import app, redirect_url
from sociometry import models as m
from sqlite3 import IntegrityError


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/list")
def list():
    classes = g.curr.execute("SELECT * FROM classes ORDER BY created DESC").fetchall()
    return render_template("list.html", classes=classes)


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static",filename="favicon.ico"))


@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        if request.form["name"] and request.form["childlist"]:
            names_list = [child.strip() for child in request.form["childlist"].split("\r\n") if child != '']
            classid = m.ClassModel.new(request.form["name"], names_list)
            return redirect(url_for("manage_gender", classid=classid))
        else:
            flash(u"Chybí název třídy nebo seznam žáků", 'danger')
    return render_template("new.html")


@app.route("/add/children/<int:classid>", methods=["POST"])
def add_children(classid):
    names_list = [child.strip() for child in request.form["childlist"].split("\r\n") if child != '']
    m.ChildrenModel.addChildren(classid, names_list)
    if request.form["redirect"] is not None:
        return redirect(request.form["redirect"])
    return redirect(url_for('view_class', classid=classid))


@app.route("/gender/<int:classid>", methods=["GET", "POST"])
def manage_gender(classid):
    #All right, he sent the data
    if request.method == "POST":
        females = [int(id) for id in request.form.getlist("females")]
        m.ChildrenModel.changeGenders(females)
        flash(u"Pohlaví nastaveno", 'success')
        if "redirect" in request.form.keys():
            return redirect(request.form["redirect"])
        return redirect(url_for('view_class', classid=classid))


    #GET stuff
    classdata = m.ClassModel.getData(classid)
    #no such class
    if classdata is None:
        flash(u"Taková třída neexistuje!", "danger")
        return redirect(url_for("index"))
    children = m.ChildrenModel.getByClass(classid)
    return render_template("gender.html", class_name=classdata["name"], children=children, classid=classid)


@app.route("/input/<int:childid>", methods=["POST", "GET"])
def questionnaire_input(childid):
    child_data = m.ChildrenModel.getData(childid)
    if child_data is None:
        flash(u"Takovýto žák neexistuje", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        insertdict = {key: value for (key, value) in request.form.items()}
        try:
            m.QuestionnaireModel.insertFromForm(childid, insertdict)
        except IntegrityError:
            flash(u"Tento žák má již dotazník vyplněn", "danger")
        return redirect(redirect_url("view_class", classid=child_data["class"]))

    cm_data = g.curr.execute("SELECT id,name FROM children WHERE class=? AND id!=? ORDER BY gender, name", [child_data["class"], childid]).fetchall()
    classmates = [{"id": child["id"], "name": child["name"]} for child in cm_data]
    return render_template("questionnaire_input.html", child=child_data, classmates=classmates, questionnaire=m.Questionnaire())


@app.route("/delete/<stuff>/<int:stuffid>")
def delete(stuff, stuffid):
    if stuff == "class":
        m.ClassModel.delete(stuffid)
        flash(u"Úspěšně smazáno", "success")
        return redirect(url_for("list"))
    if stuff == "child":
        childclass = m.ChildrenModel.getData(stuffid)["class"]
        m.ChildrenModel.delete(stuffid)
        flash(u"Úspěšně smazáno", "success")
        return redirect(url_for("view_class", classid=childclass))
    if stuff == "questionnaire":
        childclass = m.ChildrenModel.getData(stuffid)["class"]
        m.QuestionnaireModel.delete(stuffid)
        flash(u"Úspěšně smazáno", "success")
        return redirect(redirect_url("view_class", classid=childclass))
    abort(400)


@app.route("/view/class/<int:classid>")
def view_class(classid):
    classdata = m.ClassModel.getData(classid)
    children = m.ChildrenModel.getByClass(classid)
    completion = m.ClassModel.getCompletionPercentage(classid)
    return render_template("viewclass.html", classdata=classdata, children=children, completion=completion)


@app.route("/diagram/<int:classid>/<type>")
def diagram(classid, type):
    orbits = m.QuestionnaireModel.getOrbitCount(classid, type)
    load = m.DiagramModel.hasSavedDiagram(classid,type)
    return render_template("diagram.html", classid=classid, type=type, loader=load, orbits=orbits)

