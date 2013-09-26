# -*- coding: utf8 -*-
from __future__ import division
from flask import g
import time


class BaseDb(object):
    @staticmethod
    def begin():
        g.db.execute("BEGIN TRANSACTION;")

    @staticmethod
    def commit():
        g.db.commit()

    @staticmethod
    def rollback():
        g.db.rollback()


class ClassModel(BaseDb):
    u"""Class for manipulating with classes in db"""

    @staticmethod
    def new(name, names_list):
        ClassModel.begin()
        g.cur.execute("INSERT INTO classes (name, created) VALUES (?,?)", [name, time.time()])
        classid = g.cur.lastrowid
        ChildrenModel.addChildren(classid, names_list)
        ClassModel.commit()
        return classid

    @staticmethod
    def getData(classid):
        return g.cur.execute("SELECT * FROM classes WHERE id=?", [classid]).fetchone()

    @staticmethod
    def getCompletionPercentage(classid):
        data = g.cur.execute("""SELECT
            (SELECT COUNT(*) FROM children WHERE class=?),
            (SELECT COUNT(*) FROM questionnaires
                WHERE child IN (SELECT id FROM children WHERE class=?))""", [classid, classid]).fetchone()
        return (data[1]/data[0])*100

    @staticmethod
    def getAll():
        return g.cur.execute("SELECT * FROM classes ORDER BY created DESC").fetchall()

    @staticmethod
    def rename(classid, newname):
        ClassModel.begin()
        g.cur.execute("UPDATE classes SET name=? WHERE id=?", [newname, classid])
        ClassModel.commit()
        return True

    @staticmethod
    def delete(classid):
        ClassModel.begin()
        g.cur.execute("DELETE FROM friendships WHERE who IN (SELECT id FROM children WHERE class=?)", [classid])
        g.cur.execute("DELETE FROM children WHERE class=?", [classid])
        g.cur.execute("DELETE FROM classes WHERE id=?", [classid])
        ClassModel.commit()
        return True


class ChildrenModel(BaseDb):
    u"""Class for manipulating with children in db"""
    @staticmethod
    def getData(childid):
        return g.cur.execute("SELECT * FROM children WHERE id=?", [childid]).fetchone()

    @staticmethod
    def addChildren(classid, names_list):
        #list comprehension, fuck yeah!
        #I will hate myself in one year...
        ChildrenModel.begin()
        insert_list = [(classid, child.strip(), 0, cindex) for cindex, child in enumerate(names_list, 1)]
        g.cur.executemany('INSERT INTO children (class, name, gender, classid) VALUES (?,?,?,?)', insert_list)
        ChildrenModel.resetIds(classid)
        ChildrenModel.commit()
        return True

    @staticmethod
    def resetIds(classid):
        ids = g.cur.execute("SELECT id FROM children WHERE class=? ORDER BY id", [classid]).fetchall()
        update_list = [(key, value) for key, value in enumerate([row["id"] for row in ids], start=1)]
        g.cur.executemany("UPDATE children SET classid=? WHERE id=?", update_list)
        return True

    @staticmethod
    def changeGenders(female_list, gender=1):
        ChildrenModel.begin()
        updatearr = [(gender, childid) for childid in female_list]
        g.cur.executemany("UPDATE children SET gender=? WHERE id=?", updatearr)
        ChildrenModel.commit()
        return True

    @staticmethod
    def getByClass(classid):
        return g.cur.execute("""SELECT children.id AS id,class,name,gender,classid,questionnaires.id AS qid
                             FROM children LEFT JOIN questionnaires ON questionnaires.child = children.id
                             WHERE class=?""", [classid]).fetchall()

    @staticmethod
    def delete(childid):
        ChildrenModel.begin()
        childclass = g.cur.execute("SELECT class FROM children WHERE id=?", [childid]).fetchone()["class"]
        g.cur.execute("DELETE FROM children WHERE id=?", [childid])
        ChildrenModel.resetIds(childclass)
        ChildrenModel.commit()
        return True


class FriendshipModel(BaseDb):
    u"""Class for manipulating with friendships in db"""

    @staticmethod
    def new(who, likes):
        #classid = g.cur.execute("SELECT class FROM children ").fetchone()["class"]
        g.cur.execute("INSERT INTO friendships (who, likes) VALUES (?,?)", [who, likes])
        return g.cur.lastrowid

    @staticmethod
    def replaceFriendships(child, likes_list):
        FriendshipModel.begin()
        g.cur.execute("DELETE FROM friendships WHERE who=?", child)
        #No friends :-(
        if likes_list is None:
            g.db.commit()
            return True
        friendships_list = [(child, int(likes)) for likes in likes_list]
        g.cur.executemany("INSERT INTO friendships (who, likes) VALUES (?,?)", friendships_list)
        FriendshipModel.commit()


class QuestionnaireModel(BaseDb):
    u"""Model for manipulatiting questionnaire in DB"""
    @staticmethod
    def insertFromForm(childid, formdata):
        QuestionnaireModel.begin()
        formdata["child"] = childid

        q = Questionnaire()
        #For unchecked checkboxes
        for key in q.allkeys:
            if key not in formdata.keys():
                formdata[key] = None

        #for not filled selects
        for key in q.zeroisnullkeys:
            if formdata[key] == '0':
                formdata[key] = None

        g.cur.execute('''INSERT INTO questionnaires
                      (child, friend1, friend2, friend3,
                      antipathy1, antipathy2, antipathy3,
                      selfeval,
                      yesnoquest1, yesnoquest2, yesnoquest3, yesnoquest4, yesnoquest5,
                      scale1, scale2, scale3, scale4, scale5,
                      traits1, traits2, traits3, traits4, traits5,
                      traits6, traits7, traits8, traits9, traits10
                      )
                      VALUES (
                      :child, :friend1, :friend2, :friend3,
                      :antipathy1, :antipathy2, :antipathy3,
                      :selfeval,
                      :yesnoquest1, :yesnoquest2, :yesnoquest3, :yesnoquest4, :yesnoquest5,
                      :scale1, :scale2, :scale3, :scale4, :scale5,
                      :traits1, :traits2, :traits3, :traits4, :traits5,
                      :traits6, :traits7, :traits8, :traits9, :traits10)''', formdata)
        QuestionnaireModel.commit()
        return g.cur.lastrowid

    @staticmethod
    def getOrbitCount(classid, type):
            if type == "friend":
                values = g.cur.execute("""SELECT DISTINCT (SELECT COUNT(id) FROM questionnaires
                                WHERE friend1=q.child  OR friend2=q.child OR friend3=q.child) AS count
                                FROM questionnaires AS q
                                WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()
            elif type == "antipathy":
                values = g.cur.execute("""SELECT DISTINCT (SELECT COUNT(id) FROM questionnaires WHERE antipathy1=q.child  OR
                                    antipathy2=q.child OR antipathy3=q.child) AS count
                                    FROM questionnaires AS q
                                    WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()
            else:
                return None

            return len(values)


    @staticmethod
    def getDiagramData(classid, type):
        #We will return this, eventually
        return_dict = {}
        if type == "friend":
            #Selects friend counts for each child
            prefs = g.cur.execute("""SELECT q.child AS child,classid,gender,
                                        (SELECT COUNT(id) FROM questionnaires
                                        WHERE friend1=q.child  OR friend2=q.child OR friend3=q.child) AS count
                                        FROM questionnaires AS q
                                        JOIN children ON child=children.id
                                        WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()

            #SELECT only distinct counts, so we know about orbits
            values = g.cur.execute("""SELECT DISTINCT (SELECT COUNT(id) FROM questionnaires
                                WHERE friend1=q.child  OR friend2=q.child OR friend3=q.child) AS count
                                FROM questionnaires AS q
                                WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()

        #Same stuff, but for antipathy (yes, I am feeling wet :-))
        elif type == "antipathy":
            prefs = g.cur.execute("""SELECT q.child AS child,classid,gender,
                                    (SELECT COUNT(id) FROM questionnaires WHERE antipathy1=q.child  OR
                                    antipathy2=q.child OR antipathy3=q.child) AS count
                                    FROM questionnaires AS q
                                    JOIN children ON child=children.id
                                    WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()

            values = g.cur.execute("""SELECT DISTINCT (SELECT COUNT(id) FROM questionnaires WHERE antipathy1=q.child  OR
                                    antipathy2=q.child OR antipathy3=q.child) AS count
                                    FROM questionnaires AS q
                                    WHERE child IN (SELECT id FROM children WHERE class=?);""", [classid]).fetchall()

        else:
            #Nor friend, nor antipathy diagram
            return None

        #Having N friends means being on Orbit X
        #orbit_dict is conversion for N:X
        temp = [value[0] for value in values]
        temp.sort()
        temp.reverse()
        orbit_dict = ({value: key for key, value in enumerate(temp)})
        del temp

        #number of orbits
        return_dict["orbits"] = len(orbit_dict)
        return_dict["children"] = []
        for pref in prefs:
            return_dict["children"].append(
                {"classid": pref["classid"], "gender": pref["gender"], "orbit": orbit_dict[pref["count"]]}
            )

        return return_dict

    @staticmethod
    def getLinksData(classid, type):
        #we will return those
        oneway = []
        twoway = []

        #conversion between child ids and their in-class serial number.
        #We need this because links are done between javascript object with ids of those serial numbers
        id2classid = {line["id"]: line["classid"] for line in g.cur.execute("""SELECT id, classid
                                                                                FROM children WHERE class=?""", [classid]).fetchall()}

        if type == "friend":
            raw_data = g.cur.execute("""SELECT child,friend1 AS r1,friend2 AS r2,friend3 AS r3
                                        FROM questionnaires
                                        WHERE child IN (SELECT id FROM children WHERE class=?)""", [classid])
        elif type == "antipathy":
            raw_data = g.cur.execute("""SELECT child,antipathy1 AS r1, antipathy2 AS r2,antipathy3 AS r3
                                        FROM questionnaires
                                        WHERE child IN (SELECT id FROM children WHERE class=?)""", [classid])
        else:
            return None

        data = {child["child"]: [child["r1"], child["r2"], child["r3"]] for child in raw_data}
        #For every friendship we know
        for key, row in data.items():
            for item in data[key]:
                if item is None:
                    #friendship wasn't filled in
                    continue
                who = id2classid[key]
                likes = id2classid[item]
                #Check if this is mutual
                if key in data[item]:
                    #and if it isn't already there
                    if not {"likes": who, "who": likes} in twoway:
                        twoway.append({"who": who, "likes": likes})
                else:
                    oneway.append({"who": who, "likes": likes})

        return {"onewaylinks": oneway, "twowaylinks": twoway}

    @staticmethod
    def delete(qid):
        QuestionnaireModel.begin()
        g.cur.execute("DELETE FROM questionnaires WHERE child=?", [qid])
        QuestionnaireModel.commit()
        return True


class DiagramModel(BaseDb):
    @staticmethod
    def saveDiagram(classid, type, data):
        DiagramModel.begin()
        now = int(time.time())
        g.cur.execute("INSERT INTO diagrams (class,type,created,data) VALUES (?,?,?,?)", [classid, type, now, data])
        DiagramModel.commit()
        return g.cur.lastrowid

    @staticmethod
    def hasSavedDiagram(classid, type):
        return bool(g.cur.execute("""SELECT COUNT(*) AS cnt
                        FROM diagrams WHERE class=? AND type=?""", [classid, type]).fetchone()["cnt"])

    @staticmethod
    def getData(diagramid):
        return g.cur.execute("SELECT id, class, created, data FROM diagrams WHERE id=?", [diagramid]).fetchone()

    @staticmethod
    def getAllDiagrams(classid, type):
        return g.cur.execute("SELECT id, created, data FROM diagrams WHERE class=? AND type=?", [classid, type]).fetchall()

    @staticmethod
    def getLastDiagram(classid, type):
        return g.cur.execute("""SELECT id, created, data
                                FROM diagrams
                                WHERE class=? AND type=?
                                ORDER BY created DESC
                                LIMIT 1""", [classid, type]).fetchone()


class Questionnaire(object):
    u"""Class with texts of questionnaire"""
    def __init__(self):

        self.friends = [
            {"formname": "friend1",
                "label": u"Mezi přátele patří (1. volba)" },
            {"formname": "friend2",
                "label": u"Mezi přátele patří (2. volba)"},
            {"formname": "friend3",
                "label": u"Mezi přátele patří (3. volba)"},
        ]

        self.antipathy = [
            {"formname": "antipathy1",
                "label": u"Jako přítele by sis nevybral (1.volba)"},
            {"formname": "antipathy2",
                "label": u"Jako přítele by sis nevybral (2.volba)"},
            {"formname": "antipathy3",
                "label": u"Jako přítele by sis nevybral (3.volba)"},
        ]

        self.selfeval = [
            {"value": 1,
                "text": u"a) jsem vždy v centru dění"},
            {"value": 2,
                "text": u"b) občas se účastním a jsem obvykle o akcích ve třídě informován"},
            {"value": 3,
                "text": u"c) párkrát jsem se akcí ve třídě účastnil, ale nebývám informován"},
            {"value": 4,
                "text": u"d) zdá se, že o mou účast třída příliš nestojí"},
            {"value": 5,
                "text": u"e) o dění ve třídě nejevím zájem"},
        ]

        self.yesnoquest = [
            {"text": u"Ve třídě je nejméně jeden žák, který je nešťastný…",
                "formname": "yesnoquest1"},
            {"text": u"Ve třídě je někdo, komu ostatní občas ubližují…",
                "formname": "yesnoquest2"},
            {"text": u"Stává se, že se do školy těším…",
                "formname": "yesnoquest3"},
            {"text": u"Většinou se najde někdo, kdo mi pomůže s problémem…",
                "formname": "yesnoquest4"},
            {"text": u"Společné problémy řešíme většinou v klidu…",
                "formname": "yesnoquest5"},
        ]

        self.scale = [
            {"mintext": u"pocit bezpečí",
                "maxtext": u"pocit ohrožení",
                "formname": "scale1"},
            {"mintext": u"pocit přátelství",
                "maxtext": u"pocit nepřátelství",
                "formname": "scale2"},
            {"mintext": u"atmosféra spolupráce",
                "maxtext": u"atmosféra lhostejnosti",
                "formname": "scale3"},
            {"mintext": u"pocit důvěry",
                "maxtext": u"pocit nedůvěry",
                "formname": "scale4"},
            {"mintext": u"tolerance",
                "maxtext": u"netolerance",
                "formname": "scale5"},
        ]

        self.traits = [
            {"text": u"spravedlivý",
                "formname": "traits1"},
            {"text": u"spolehlivý",
                "formname": "traits2"},
            {"text": u"zábavný",
                "formname": "traits3"},
            {"text": u"vždy v centru dění",
                "formname": "traits4"},
            {"text": u"se všemi zadobře",
                "formname": "traits5"},
            {"text": u"protivný",
                "formname": "traits6"},
            {"text": u"nespravedlivý",
                "formname": "traits7"},
            {"text": u"nevděčný",
                "formname": "traits8"},
            {"text": u"nespolehlivý",
                "formname": "traits9"},
            {"text": u"osamocený",
                "formname": "traits10"},
        ]

        self.allkeys = ["friend1", "friend2", "friend3",
                        "antipathy1", "antipathy2", "antipathy3",
                        "selfeval",
                        "yesnoquest1", "yesnoquest2", "yesnoquest3", "yesnoquest4", "yesnoquest5",
                        "scale1", "scale2", "scale3", "scale4", "scale5",
                        "traits1", "traits2", "traits3", "traits4", "traits5",
                        "traits6", "traits7", "traits8", "traits9", "traits10"]

        self.zeroisnullkeys = ["friend1", "friend2", "friend3",
                      "antipathy1", "antipathy2", "antipathy3",
                      "selfeval",
                      "traits1", "traits2", "traits3", "traits4", "traits5",
                      "traits6", "traits7", "traits8", "traits9", "traits10"]