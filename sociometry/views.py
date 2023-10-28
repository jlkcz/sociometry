# -*- coding: utf8 -*-
from __future__ import print_function, generators
from flask import url_for, render_template, request, request, flash, redirect, abort, Response, current_app, after_this_request, send_file
from sociometry import app, redirect_url, models as m, exports as e
from sqlite3 import IntegrityError
from werkzeug.datastructures import Headers

@app.route("/")
def index():
    classes = m.ClassModel.getAll()
    return render_template("index.html", classes=classes)


@app.route("/list")
def list():
    classes = m.ClassModel.getAll()
    return render_template("list.html", classes=classes)


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))


@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        if request.form["name"] and request.form["childlist"]:
            names_list = [child.strip() for child in request.form["childlist"].split("\r\n") if child.strip() != '']
            classid = m.ClassModel.new(request.form["name"], names_list, request.form["missing"])
            flash(u"Třída úspěšně vytvořena", "success")
            return redirect(url_for("manage_gender", classid=classid))
        else:
            flash(u"Chybí název třídy nebo seznam žáků", 'warning')
    return render_template("new.html")


@app.route("/add/children/<int:classid>", methods=["POST"])
def add_children(classid):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if m.ClassModel.isClosed(classid):
            flash(u"Tato třída je uzavřená, nelze přidávat žáky!", "danger")
            return redirect(url_for('view_class', classid=classid))
    names_list = [child.strip() for child in request.form["childlist"].split("\r\n") if child != '']
    m.ChildrenModel.addChildren(classid, names_list)
    flash(u"Žáci úspěšně přidáni", "success")
    return redirect(url_for('view_class', classid=classid))


@app.route("/gender/<int:classid>", methods=["GET", "POST"])
def manage_gender(classid):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if m.ClassModel.isClosed(classid):
        flash(u"Tato třída je uzavřená, nelze měnit pohlaví žáků!", "danger")
        return redirect(url_for('view_class', classid=classid))
    if request.method == "POST":
        females = [int(id) for id in request.form.getlist("females")]
        m.ChildrenModel.changeGenders(females)
        flash(u"Pohlaví nastaveno", 'success')
        return redirect(url_for('view_class', classid=classid))

    #GET stuff
    classdata = m.ClassModel.getData(classid)
    children = m.ChildrenModel.getByClass(classid)
    return render_template("gender.html", class_name=classdata["name"], children=children, classid=classid)


@app.route("/input/<int:childid>", methods=["POST", "GET"])
def questionnaire_input(childid):
    if not m.ChildrenModel.exists(childid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
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
    #GET
    classmates = m.ClassModel.getClassmates(child_data["class"], childid)
    return render_template("questionnaire_input.html", child=child_data, classmates=classmates, questionnaire=m.Questionnaire())

@app.route("/update/questionnaire/<int:qid>", methods=["POST"])
def update_questionnaire(qid):
    insertdict = {key: value for (key, value) in request.form.items()}
    updated = m.QuestionnaireModel.updateQuestionnaire(insertdict, qid)
    if updated:
        flash(u"Dotazník úspěšně změněn", u"success")
    else:
        flash(u"Takový dotazník neexistuje", u"warning")
    return redirect(url_for("view_questionnaire", childid=insertdict["child"]))

@app.route("/delete/<stuff>/<int:stuffid>")
def delete(stuff, stuffid):
    if stuff == "class":
        #we can delete whole class without checking, it just disappears
        m.ClassModel.delete(stuffid)
        flash(u"Úspěšně smazáno", "success")
        return redirect(url_for("list"))

    if stuff == "child":
        childclass = m.ChildrenModel.getData(stuffid)["class"]
        if m.ChildrenModel.delete(stuffid):
            flash(u"Úspěšně smazáno", "success")
            return redirect(url_for("view_class", classid=childclass))
        else:
            flash(u"Žák neexistuje nebo je jeho třída uzavřená, nelze mazat dotazníky", "danger")
            return redirect(url_for("list"))

    if stuff == "questionnaire":
        if m.QuestionnaireModel.delete(stuffid):
            flash(u"Úspěšně smazáno", "success")
            childclass = m.ChildrenModel.getData(stuffid)["class"]
            return redirect(redirect_url("view_class", classid=childclass))
        else:
            flash(u"Dotazník neexistuje nebo je jeho třída uzavřená, nelze mazat dotazníky", "danger")
            return redirect(url_for("list"))
    abort(400)


@app.route("/view/class/<int:classid>")
def view_class(classid):
    classdata = m.ClassModel.getData(classid)
    if classdata is None:
        flash("Taková třída neexistuje")
        return redirect(url_for("index"))

    children = m.ChildrenModel.getByClass(classid)

    #Hacks for empty class
    empty = False
    if len(children) == 0:
        empty = True
    try:
        completion = m.ClassModel.getCompletionPercentage(classid)
    except ZeroDivisionError:
        completion = 0
    return render_template("viewclass.html", classdata=classdata, children=children, completion=completion, empty=empty)


@app.route("/view/questionnaire/<int:childid>")
def view_questionnaire(childid):
    child_data = m.ChildrenModel.getData(childid)
    if child_data is None:
        flash(u"Takovýto žák neexistuje", "danger")
        return redirect(url_for("index"))
    questionnaire_data = m.QuestionnaireModel.getData(childid)
    if questionnaire_data is None:
        flash(u"Takovýto žák neexistuje", "danger")
        return redirect(url_for("view_class", classid=child_data["class"]))
    classmates = m.ClassModel.getClassmates(child_data["class"], childid)
    return render_template("questionnaire_input.html", child=child_data, filled=questionnaire_data, questionnaire=m.Questionnaire, classmates=classmates)


@app.route("/modify/child/<int:childid>", methods=["POST"])
def modify_child(childid):
    if not (childid and request.form["newname"]):
        flash(u"Jméno žáka nesmí být prázdné!", "danger")
        return redirect(url_for("view_class", classid=request.form["classid"]) + "?tab=children")
    changed = m.ChildrenModel.changeName(childid, request.form["newname"])
    if changed:
        flash(u"Dítě úspěšně změněno","success")
    else:
        flash(u"Takové dítě neexistuje","warning")
    return redirect(url_for("view_class", classid=request.form["classid"]) + "?tab=pupils")


@app.route("/modify/class/<int:classid>", methods=["POST"])
def modify_class(classid):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if m.ClassModel.isClosed(classid):
        flash(u"Třída je uzavřená, nelze ji upravovat", "warning")
        return redirect(url_for("index"))
    #check if the request is sane
    if request.form["missing"].isdigit() and request.form["name"]:
        m.ClassModel.modify(classid, request.form["name"], request.form["missing"])
        flash(u"Úspěšně změněno", "success")
    else:
        flash(u"Špatně zadané hodnoty", "danger")
    return redirect(url_for("view_class", classid=classid))


@app.route("/close/class/<int:classid>")
def close_class(classid):
    #we can close already closed class, no harm is done
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if m.ClassModel.getCompletionPercentage(classid) != 100:
        flash(u"Třídu nelze uzavřít, nemá vyplněné všechny dotazníky!", "danger")
        return redirect(url_for("view_class", classid=classid))
    else:
        m.ClassModel.close(classid)
        flash(u"Třída úspěšně uzavřena. Nyní se můžete podívat na sociogramy či stáhnout výstup", "success")
    return redirect(url_for("view_class", classid=classid))


@app.route("/reopen/class/<int:classid>")
def reopen_class(classid):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    m.ClassModel.reopen(classid)
    return redirect(url_for("view_class", classid=classid))


@app.route("/diagram/<int:classid>/<type>")
def diagram(classid, type):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if not m.ClassModel.isClosed(classid):
        flash(u"Tato třída ještě není uzavřená, nelze si prohlížet sociogramy", "danger")
        return redirect(url_for("view_class", classid=classid))
    orbit_nums = m.QuestionnaireModel.getOrbitNums(classid, type)
    orbits = len(orbit_nums)
    load = m.DiagramModel.hasSavedDiagram(classid, type)

    return render_template("diagram.html", classid=classid, type=type, loader=load, orbits=orbits)


@app.route("/export/class/<int:classid>")
def export_class(classid):
    if not m.ClassModel.exists(classid):
        flash(u"Taková třída neexistuje", "warning")
        return redirect(url_for("index"))
    if not m.ClassModel.isClosed(classid):
        flash(u"Tato třída ještě není uzavřená, nelze ji exportovat", "danger")
        return redirect(url_for("view_class", classid=classid))
    export = e.ClassExporter(classid, current_app.config["ALLOW_B3"])
    export.export()
    return send_file(export.file, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",download_name=export.filename, as_attachment=True)


@app.route("/get/png/<key>")
def get_png(key):
    data = m.TempfileModel.use_and_burn(key)
    response = Response(data["data"])
    response.headers = Headers({
            'Pragma': "public",  # required,
            'Expires': '0',
            'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
            'Cache-Control': 'private',  # required for certain browsers,
            'Content-Type': "image.png",
            'Content-Disposition': 'attachment; filename=\"{}.png\";'.format(data["filename"]),
            'Content-Transfer-Encoding': 'binary',
            'Content-Length': len(response.data)
    })
    return response

@app.route("/sociometry-shutdown")
def shutdown():
    response = Response(render_template("shutdown.html"))
    @response.call_on_close
    def shutdown_server():
        import os
        import signal
        import time
        time.sleep(3)
        os.kill(os.getpid(), signal.SIGINT)
    return response
