# -*- coding: utf8 -*-
u"""Contains model (DB) classes (static methods). """
#Naming conventions are bit cranky (my PHP skills are interfering, but I am working on it)

from __future__ import division, print_function
from flask import g
import time
import hashlib


class BaseDb(object):
    u"""Abstract class providing transaction operations"""
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
    def new(name, names_list, missing=0):
        ClassModel.begin()
        g.cur.execute("INSERT INTO classes (name, created, missing) VALUES (?,?,?)", [name, time.time(), missing])
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
    def exists(classid):
        if g.cur.execute("SELECT * FROM classes WHERE id=?", [classid]).fetchone() is None:
            return False
        return True

    @staticmethod
    def getAll():
        return g.cur.execute("SELECT * FROM classes ORDER BY created DESC").fetchall()

    @staticmethod
    def isClosed(classid):
        return bool(g.cur.execute("SELECT closed FROM classes WHERE id=?", [classid]).fetchone()[0])

    @staticmethod
    def close(classid):
        ClassModel.begin()
        g.cur.execute("UPDATE classes SET closed=1 WHERE id=?", [classid])
        ClassModel.commit()
        return True

    @staticmethod
    def reopen(classid):
        ClassModel.begin()
        g.cur.execute("DELETE FROM diagrams WHERE class=?", [classid])
        g.cur.execute("UPDATE classes SET closed=0 WHERE id=?", [classid])
        ClassModel.commit()
        return True

    @staticmethod
    def modify(classid, newname, missing=0):
        ClassModel.begin()
        g.cur.execute("UPDATE classes SET name=?, missing=? WHERE id=?", [newname, missing, classid])
        ClassModel.commit()
        return True

    @staticmethod
    def delete(classid):
        ClassModel.begin()
        g.cur.execute("DELETE FROM friendships WHERE who IN (SELECT id FROM children WHERE class=?)", [classid])
        g.cur.execute("DELETE FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=?)", [classid])
        g.cur.execute("DELETE FROM diagrams WHERE class=?", [classid])
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
    def exists(childid):
        if ChildrenModel.getData(childid) is None:
            return False
        return True

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
                             WHERE class=? ORDER BY classid""", [classid]).fetchall()

    @staticmethod
    def delete(childid):
        ChildrenModel.begin()
        try:
            childclass = g.cur.execute("SELECT class FROM children WHERE id=?", [childid]).fetchone()["class"]
        except TypeError:
            return False
        if ClassModel.isClosed(childclass):
            return False
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

        #For unchecked checkboxes
        for key in Questionnaire.allkeys:
            if key not in formdata.keys():
                formdata[key] = None

        #for not filled selects
        for key in Questionnaire.zeroisnullkeys:
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
                                WHERE child IN (SELECT id FROM children WHERE class=?) ORDER BY count ASC""", [classid]).fetchall()

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
                                    WHERE child IN (SELECT id FROM children WHERE class=?) ORDER BY count ASC""", [classid]).fetchall()
        else:
            #Not friend, nor antipathy diagram
            return None

        #Having N friends means being on Orbit X
        #orbit_dict is conversion for N:
        temp = [value[0] for value in values]
        temp.sort()
        temp.reverse()
        if temp[-1] == 0:
            zeroorbit = True
        else:
            zeroorbit = False
        orbit_dict = ({value: key for key, value in enumerate(temp)})
        del temp

        #number of orbits
        return_dict["orbits"] = len(orbit_dict)
        return_dict["zeroorbit"] = zeroorbit
        return_dict["children"] = []
        for pref in prefs:
            return_dict["children"].append(
                {"classid": pref["classid"], "gender": pref["gender"], "orbit": orbit_dict[pref["count"]]}
            )
        return return_dict

    @staticmethod
    def getQualitativeData(classid, order_by_hierarchy=None):
        if order_by_hierarchy is None:
            order_by = "ORDER BY classid ASC"
        elif order_by_hierarchy is True:
            order_by = "ORDER BY hierarchy DESC"
        elif order_by_hierarchy is False:
            order_by = "ORDER BY  attractivity DESC"
        return g.cur.execute("""SELECT
                                    *,
                                    positive + negative AS attractivity,
                                    positive - negative AS hierarchy
                                FROM(
                                    SELECT
                                        *,
                                        friend1*3 + friend2*2 + friend3 + traits1 + traits2 + traits3 + traits4 + traits5 AS positive,
                                        antipathy1*3 + antipathy2*2 + antipathy3 + traits6 + traits7 + traits8 + traits9 + traits10 AS negative,
                                        friend1 + friend2 + friend3 AS friendships,
                                        antipathy1 + antipathy2 + antipathy3 AS antipathies
                                    FROM
                                    (
                                         SELECT id, name, classid,
                                        (SELECT COUNT(*) FROM questionnaires WHERE friend1=c.id) AS friend1,
                                        (SELECT COUNT(*) FROM questionnaires WHERE friend2=c.id) AS friend2,
                                        (SELECT COUNT(*) FROM questionnaires WHERE friend3=c.id) AS friend3,
                                        (SELECT COUNT(*) FROM questionnaires WHERE antipathy1=c.id) AS antipathy1,
                                        (SELECT COUNT(*) FROM questionnaires WHERE antipathy2=c.id) AS antipathy2,
                                        (SELECT COUNT(*) FROM questionnaires WHERE antipathy3=c.id) AS antipathy3,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits1=c.id) AS traits1,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits2=c.id) AS traits2,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits3=c.id) AS traits3,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits4=c.id) AS traits4,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits5=c.id) AS traits5,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits6=c.id) AS traits6,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits7=c.id) AS traits7,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits8=c.id) AS traits8,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits9=c.id) AS traits9,
                                        (SELECT COUNT(*) FROM questionnaires WHERE traits10=c.id) AS traits10,
                                        (SELECT selfeval FROM questionnaires WHERE child=c.id) AS selfeval,
                                        (SELECT scale1+scale2+scale3+scale4+scale5 FROM questionnaires WHERE child=c.id) AS scale,
                                        (SELECT yesnoquest1 FROM questionnaires WHERE child=c.id) AS yesnoquest1,
                                        (SELECT yesnoquest2 FROM questionnaires WHERE child=c.id) AS yesnoquest2,
                                        (SELECT yesnoquest3 FROM questionnaires WHERE child=c.id) AS yesnoquest3,
                                        (SELECT yesnoquest4 FROM questionnaires WHERE child=c.id) AS yesnoquest4,
                                        (SELECT yesnoquest5 FROM questionnaires WHERE child=c.id) AS yesnoquest5
                                        FROM children AS c
                                        WHERE class=?
                                    )
                                ) """ + order_by, [classid]).fetchall()


    @staticmethod
    def getQuantitativeData(classid):
        return g.cur.execute("""SELECT missing,
                    (SELECT COUNT(*) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS children_count,
                    (SELECT SUM(scale1+scale2+scale3+scale4+scale5) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS positive_feelings,
                    (SELECT SUM(result) FROM(
                        SELECT
                        	CASE WHEN yesnoquest1=0 OR yesnoquest1 IS NULL THEN 1 ELSE 0 END +
                        	CASE WHEN yesnoquest2=0 OR yesnoquest2 IS NULL THEN 1 ELSE 0 END +
                        	CASE WHEN yesnoquest3=0 OR yesnoquest3 IS NULL THEN 0 ELSE 1 END +
                        	CASE WHEN yesnoquest4=0 OR yesnoquest4 IS NULL THEN 0 ELSE 1 END +
                        	CASE WHEN yesnoquest5=0 OR yesnoquest5 IS NULL THEN 0 ELSE 1 END
                        AS Result
                        FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid))) AS quality,
                    (SELECT COUNT(*)/2 AS count FROM (
                        SELECT DISTINCT A.child,A.friend,B.friend,B.child FROM (
                            SELECT child, friend1 AS friend FROM questionnaires WHERE friend1 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, friend2 AS friend FROM questionnaires WHERE friend2 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, friend3 AS friend FROM questionnaires WHERE friend3 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                        ) A
                        INNER JOIN (
                            SELECT child, friend1 AS friend FROM questionnaires WHERE friend1 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, friend2 AS friend FROM questionnaires WHERE friend2 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, friend3 AS friend FROM questionnaires WHERE friend3 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                        ) B
                        WHERE A.child=B.friend AND B.child=A.friend
                    )) AS bidirectional_friends,
                                        (SELECT COUNT(*)/2 AS count FROM (
                        SELECT DISTINCT A.child,A.antipathy,B.antipathy,B.child FROM (
                            SELECT child, antipathy1 AS antipathy FROM questionnaires WHERE antipathy1 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, antipathy2 AS antipathy FROM questionnaires WHERE antipathy2 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, antipathy3 AS antipathy FROM questionnaires WHERE antipathy3 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                        ) A
                        INNER JOIN (
                            SELECT child, antipathy1 AS antipathy FROM questionnaires WHERE antipathy1 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, antipathy2 AS antipathy FROM questionnaires WHERE antipathy2 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                            UNION
                            SELECT child, antipathy3 AS antipathy FROM questionnaires WHERE antipathy3 IS NOT NULL AND child IN (SELECT id FROM children WHERE class=:classid)
                        ) B
                        WHERE A.child=B.antipathy AND B.child=A.antipathy
                    )) AS bidirectional_antipathys,
                    (SELECT SUM(scale1) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS scale1,
                    (SELECT SUM(scale2) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS scale2,
                    (SELECT SUM(scale3) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS scale3,
                    (SELECT SUM(scale4) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS scale4,
                    (SELECT SUM(scale5) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS scale5,
                    (SELECT SUM(yesnoquest1) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS yesnoquest1,
                    (SELECT SUM(yesnoquest2) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS yesnoquest2,
                    (SELECT SUM(yesnoquest3) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS yesnoquest3,
                    (SELECT SUM(yesnoquest4) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS yesnoquest4,
                    (SELECT SUM(yesnoquest5) FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid)) AS yesnoquest5,
                    (SELECT SUM(result) FROM(
                        SELECT CASE WHEN friend1 IS NULL THEN 0 ELSE 1 END + CASE WHEN friend2 IS NULL THEN 0 ELSE 1 END + CASE WHEN friend3 IS NULL THEN 0 ELSE 1 END AS Result
                        FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid))) AS friend_all,
                    (SELECT SUM(result) FROM(
                        SELECT CASE WHEN antipathy1 IS NULL THEN 0 ELSE 1 END + CASE WHEN antipathy2 IS NULL THEN 0 ELSE 1 END + CASE WHEN antipathy3 IS NULL THEN 0 ELSE 1 END AS Result
                        FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid))) AS antipathy_all,
                    (SELECT SUM(result) FROM(
                        SELECT CASE WHEN traits1 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits2 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits3 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits4 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits5 IS NULL THEN 0 ELSE 1 END AS Result
                        FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid))) AS traits_positive,
                    (SELECT SUM(result) FROM(
                        SELECT CASE WHEN traits6 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits7 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits8 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits9 IS NULL THEN 0 ELSE 1 END + CASE WHEN traits10 IS NULL THEN 0 ELSE 1 END AS Result
                        FROM questionnaires WHERE child IN (SELECT id FROM children WHERE class=:classid))) AS traits_negative,
                    (SELECT COUNT(*) FROM questionnaires WHERE yesnoquest1=0 AND yesnoquest2=1 AND child IN (SELECT id FROM children WHERE classid=:classid)) AS empathy
                      FROM classes WHERE id=:classid""", {"classid": classid}).fetchone()
        pass


    @staticmethod
    def getRelationships(classid):
        return g.cur.execute("""SELECT child, friend1, friend2, friend3, antipathy1, antipathy2, antipathy3
                            FROM questionnaires
                            WHERE child IN (SELECT id FROM children WHERE class=?)""", [classid]).fetchall()

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
    def delete(childrenid):
        QuestionnaireModel.begin()

        try:
            classid = g.cur.execute("""SELECT class
                                        FROM children
                                        WHERE children.id=?""", [childrenid]).fetchone()["class"]
        except TypeError:
            return False

        if ClassModel.isClosed(classid):
            return False

        g.cur.execute("DELETE FROM questionnaires WHERE child=?", [childrenid])
        QuestionnaireModel.commit()
        return True


class DiagramModel(BaseDb):
    u"""Class for manipulating with diagrams"""
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


class TempfileModel(BaseDb):
    u"""Temporary file storage"""
    @staticmethod
    def store_file(filename, content):
        TempfileModel.begin()
        key = hashlib.md5(filename+str(time.time())).hexdigest()
        g.cur.execute("INSERT INTO tempfiles (filename, hash, data) VALUES (?,?,?)", [filename, key, content])
        TempfileModel.commit()
        return key

    @staticmethod
    def use_and_burn(hash):
            TempfileModel.begin()
            data = g.cur.execute("SELECT * FROM tempfiles WHERE hash=?", [hash]).fetchone()
            g.cur.execute("DELETE FROM tempfiles WHERE hash=?", [hash])
            TempfileModel.commit()
            return data


class Questionnaire(object):
    u"""Class with texts of questionnaire"""
    def __init__(self):
        pass

    friends = [
        {"formname": "friend1",
            "label": u"Mezi přátele patří (1. volba)" },
        {"formname": "friend2",
            "label": u"Mezi přátele patří (2. volba)"},
        {"formname": "friend3",
            "label": u"Mezi přátele patří (3. volba)"},
    ]

    antipathy = [
        {"formname": "antipathy1",
            "label": u"Jako přítele by sis nevybral (1.volba)"},
        {"formname": "antipathy2",
            "label": u"Jako přítele by sis nevybral (2.volba)"},
        {"formname": "antipathy3",
            "label": u"Jako přítele by sis nevybral (3.volba)"},
    ]

    selfeval = [
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

    yesnoquest = [
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

    scale = [
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

    traits = [
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

    allkeys = ["friend1", "friend2", "friend3",
                        "antipathy1", "antipathy2", "antipathy3",
                        "selfeval",
                        "yesnoquest1", "yesnoquest2", "yesnoquest3", "yesnoquest4", "yesnoquest5",
                        "scale1", "scale2", "scale3", "scale4", "scale5",
                        "traits1", "traits2", "traits3", "traits4", "traits5",
                        "traits6", "traits7", "traits8", "traits9", "traits10"]

    zeroisnullkeys = ["friend1", "friend2", "friend3",
                      "antipathy1", "antipathy2", "antipathy3",
                      "selfeval",
                      "traits1", "traits2", "traits3", "traits4", "traits5",
                      "traits6", "traits7", "traits8", "traits9", "traits10"]

    positivetraits = ["traits1", "traits2", "traits3", "traits4", "traits5"]

    negativetraits = ["traits6", "traits7", "traits8", "traits9", "traits10"]

    selfeval_inttochar = {
        1: "a",
        2: "b",
        3: "c",
        4: "d",
        5: "e",
        None: ""
    }

    yesno_toint = {
        "yesnoquest1": {1: 0, 0:1, None: 0},
        "yesnoquest2": {1: 0, 0: 1, None: 0},
        "yesnoquest3": {1: 1, 0: 0, None: 0},
        "yesnoquest4": {1: 1, 0: 0, None: 0},
        "yesnoquest5": {1: 1, 0: 0, None: 0}
    }