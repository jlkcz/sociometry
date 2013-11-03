# -*- coding: utf8 -*-
###############################################################
# Disclaimer:                                                 #
# This file is extremely ugly and I know it, unfortunately,   #
# there is very specific output and I wanted to do it right   #
# even with formatting (OMG, I am so stupid!)                 #
###############################################################

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import models as m
import datetime
import StringIO

def eiz(value):
    u"""Empty-if-zero: Return empty string if zero"""
    if value == 0:
        return ""
    return value


class ClassExporter(object):
    u"""Exports class to xlsx file"""
    #####################
    ### Magic methods ###
    #####################
    def __init__(self, classid):
        self.classdata = m.ClassModel.getData(classid)
        self.filename = self.makeSafeFilename(self.classdata["name"]) + '.xlsx'
        self.file = StringIO.StringIO()
        self.workbook = xlsxwriter.Workbook(self.file, {'default_date_format': 'dd. mm. yy'})
        #Add all worksheets. Order is important
        self.worksheet_overview = self.workbook.add_worksheet(name=u"Přehled")
        self.worksheet_quantitative = self.workbook.add_worksheet(name=u"Kvantitativní")
        self.worksheet_qualitative = self.workbook.add_worksheet(name=u"Kvalitativní")
        self.worksheet_relationships = self.workbook.add_worksheet(name=u"Sociometrie")

    ##############################
    ### Private methods helper ###
    ##############################

    def __cs(self, styledict):
        u"""Helper function for creating styles more dynamically"""
        styledict["font_name"] = "Arial"
        return self.workbook.add_format(styledict)

    def _finish(self):
        u"""Closes excel file so it's written on disk"""
        self.workbook.close()

    ############################
    ### Private main methods ###
    ############################
    def _writeRelationshipTable(self, row, col, children, relationships):
        u"""Writes relationships from array to excel table"""
        worksheet = self.worksheet_relationships
        std_style = self.__cs({"top": 1, "bottom": 1, "left": 4, "right": 4, "font": "Arial", "size": 10, "align": "center"})
        bold_style = self.__cs({"bold": True, "top": 1, "bottom": 1, "left": 4, "right": 4, "font": "Arial", "size": 10, "align": "center"})
        rotated_style = self.__cs({"rotation": 90, "bold": False, "top": 1, "bottom": 1, "left": 4, "right": 4, "font": "Arial", "size": 10, "align": "center"})

        id2column = {}
        worksheet.set_column(0, 0, 2)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 60, 2.5)

        #Write numbers on top
        for x in range(1, len(children)+1):
            worksheet.write_number(row, col+x, x, std_style)
        row += 1

        #Insert styles in empty tables
        for x in range(1, len(children)+1):
            worksheet.write_row(row+x, 1, [""]*(len(children)+1), std_style)
        #insert style in table 0,0 cell
        worksheet.write(row, col, "", std_style)

        #write child names
        for inc, childid in enumerate(sorted(children.keys()), start=1):
            childdata = children[childid]
            worksheet.write(row+inc, col, childdata["name"], std_style)
            worksheet.write(row, col+inc, childdata["name"], rotated_style)
            worksheet.set_row(row, 80)
            id2column[childid] = col+inc

        #Write relationship data

        for inc, childid in enumerate(sorted(children.keys()), start=1):
            for friend in relationships[childid].keys():
                #skippen not-filled friends
                if friend is None:
                    continue
                worksheet.write_number(row+inc, id2column[friend], relationships[childid][friend], std_style)
            worksheet.write(row+inc, 0, inc, std_style)
            worksheet.write_string(row+inc, id2column[childid], "X", std_style)

        inc += 1
        #Write sum formulas to the bottom
        for i in range(1, len(children)+1):
            height = len(children)
            worksheet.write_formula(row+inc, col+i, '=SUM({}:{})'.format(
                xl_rowcol_to_cell(row+1, col+i),
                xl_rowcol_to_cell(row+height, col+i)
            ), bold_style)
        inc += 1

        #we return our height
        return inc+1

    def _writeSociometryTable(self):
        u"""Writes both friendships and antipathies sociometry table to Excel file"""
        worksheet = self.worksheet_relationships
        children = m.ChildrenModel.getByClass(self.classdata["id"])
        relationships = m.QuestionnaireModel.getRelationships(self.classdata["id"])
        header_style = self.__cs({"font_size": 12, "bold": True, "align": "center", "font": "Arial"})

        #rearrange acquired data
        children = {child["id"]: {"name": child["name"]} for child in children}
        #Map friends to values we want to export (the better friend the higher number)
        friendships = {child["child"]: {child["friend1"]: 3, child["friend2"]: 2, child["friend3"]: 1} for child in relationships}
        antipathies = {child["child"]: {child["antipathy1"]: 3, child["antipathy2"]: 2, child["antipathy3"]: 1} for child in relationships}
        #
        #Start writting =======================
        #
        #first, we skip Oth row and column
        col = 1
        row = 1
        worksheet.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col),
            xl_rowcol_to_cell(row, col+len(children))), u'Přátelské vztahy', header_style)

        #Jump to another row
        row += 1
        #writeRelationshipTable returns number of lines we want to skip
        # also writes the relationship table :-)
        row += self._writeRelationshipTable(row, col, children, friendships)

        worksheet.set_row(row, 20)
        #Skip one line between
        row += 1

        worksheet.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col),
            xl_rowcol_to_cell(row, col+len(children))), u'Antipatie', header_style)
        row += 1
        self._writeRelationshipTable(row, col, children, antipathies)

    def _writeOverviewTable(self):
        u"""Writes overview table to Excel file"""
        ws = self.worksheet_overview
        #set width
        ws.set_column(0, 2, 2)
        ws.set_column(3, 3, 18)
        ws.set_column(4, 10, 2)
        ws.set_column(11, 11, 16)
        ws.set_column(12, 12, 10)
        ws.set_column(13, 20, 2)
        ws.set_column(21, 24, 4)

        #write headers
        ws.merge_range("A1:H1", u'Dotazník B3 - přehled', self.__cs({"bold": True, "size": 10}))
        ws.write_string("L1", self.classdata["name"], self.__cs({"bold": True, "size": 10}))
        ws.merge_range("T1:W1", u'Sebráno: ' + unicode(datetime.datetime.fromtimestamp(self.classdata["created"]).strftime("%d.%m.%Y")), self.__cs({"bold": True, "size": 10}))

        row = 2
        col = 0
        ws.set_row(row, 80)
        headers = [u"Kladné pocity", u"sebehodnocení", u"pohled na třídu", u"Kladné volby 3, 2, 1 bod", u"orbita",
                    u"spravedlivý", u"spolehlivý", u"zábavný", u"vždy v centru", u"se všemi",u"",
                    u"Seznam žáků tříd", u"Záporné volby 3, 2, 1 bod", u"orbita", u"protivný",
                    u"nespravedlivý", u"nevděčný", u"nespolehlivý", u"osamocený", u"+", u"-", u"Σ", u"φ"]
        #Columns with not rotated headers
        not_rotated = [11, 19, 20, 21, 22]
        for inc, header in enumerate(headers):
            style = self.__cs({"size": 10, "align": "center", "valign": "vcenter", "text_wrap": True, "border": 1})
            if inc not in not_rotated:
                style.set_rotation(90)
            ws.write(row, col+inc, header, style)

        row = 3
        data = m.QuestionnaireModel.getQualitativeData(self.classdata["id"])
        friendships = set()
        antipathies = set()
        for line in data:
            friendships.add(line["friendships"])
            antipathies.add(line["antipathies"])

        #Make sure that we will start with orbit 0 if there is someone who has no links
        if sorted(friendships)[0] == 0:
            fr_start = 0
        else:
            fr_start = 1
        if sorted(antipathies)[0] == 0:
            an_start = 0
        else:
            an_start = 1

        #obsolete as we now need real number, not renumbered to orbits
        #friendships2orbit = {value: key for key, value in enumerate(sorted(friendships), start=fr_start)}
        #antipathies2orbit = {value: key for key, value in enumerate(sorted(antipathies), start=an_start)}

        def_style_dict = {
            "font": "Arial",
            "size": 10,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
            "top": 1,
            "bottom": 1,
            "left": 4,
            "right": 4}
        def_style = self.__cs(def_style_dict)
        #since Format class does not support copying
        #TODO: implement copy and deepcopy for xlsxwriter.Format
        posi_style = self.__cs(def_style_dict)
        posi_style.set_bg_color("#B3FFB3")
        nega_style = self.__cs(def_style_dict)
        nega_style.set_bg_color("#FFD670")
        rend_style = self.__cs(def_style_dict)
        rend_style.set_right(1)
        lend_style = self.__cs(def_style_dict)
        lend_style.set_left(1)

        #write lines
        for inc, line in enumerate(data):
            friend_str = ','.join("3"*line["friend1"] + "2"*line["friend2"]+ "1"*line["friend3"])
            antipathy_str = ','.join("3"*line["antipathy1"] + "2"*line["antipathy2"] + "1"*line["antipathy3"])
            yesnosum = sum([m.Questionnaire.yesno_toint[item][line[item]] for item in ["yesnoquest1", "yesnoquest2", "yesnoquest3", "yesnoquest4", "yesnoquest5"]])
            #Kladné pocity
            ws.write(row+inc, 0, line["scale"], lend_style)
            #Sebehodnocení
            ws.write(row+inc, 1, m.Questionnaire.selfeval_inttochar[line["selfeval"]], def_style)
            #pohled na třídu
            ws.write(row+inc, 2, yesnosum, def_style)
            #Kladné body
            ws.write(row+inc, 3, friend_str, posi_style)
            #Orbita
            #ws.write(row+inc, 4, eiz(friendships2orbit[line["friendships"]]), def_style)
            ws.write(row+inc, 4, eiz(line["friendships"]), def_style)
            #traits...
            ws.write(row+inc, 5, eiz(line["traits1"]), posi_style)
            ws.write(row+inc, 6, eiz(line["traits2"]), posi_style)
            ws.write(row+inc, 7, eiz(line["traits3"]), posi_style)
            ws.write(row+inc, 8, eiz(line["traits4"]), posi_style)
            ws.write(row+inc, 9, eiz(line["traits5"]), posi_style)

            ws.write(row+inc, 10, line["classid"], def_style)
            #Jméno žáka
            ws.write(row+inc, 11, line["name"], def_style)
            #záporné body
            ws.write(row+inc, 12, antipathy_str, nega_style)
            #orbita
            #ws.write(row+inc, 13, eiz(antipathies2orbit[line["antipathies"]]), def_style)
            ws.write(row+inc, 13, eiz(line["antipathies"]), def_style)
            #traits
            ws.write(row+inc, 14, eiz(line["traits6"]), nega_style)
            ws.write(row+inc, 15, eiz(line["traits7"]), nega_style)
            ws.write(row+inc, 16, eiz(line["traits8"]), nega_style)
            ws.write(row+inc, 17, eiz(line["traits9"]), nega_style)
            ws.write(row+inc, 18, eiz(line["traits10"]), nega_style)
            #+
            ws.write(row+inc, 19, line["positive"], posi_style)
            #-
            ws.write(row+inc, 20, line["negative"], nega_style)
            #SUM
            ws.write(row+inc, 21, line["attractivity"], def_style)
            #DIFF
            ws.write(row+inc, 22, line["hierarchy"], rend_style)

    def _writeQualitativeTable(self):
        u"""Writes qualitative table from DB to Excel"""
        ws = self.worksheet_qualitative
        row = 0
        col = 0
        #column widths
        ws.set_column(0, 0, 10)
        ws.set_column(1, 1, 20)
        ws.set_column(2, 2, 10)
        ws.set_column(3, 3, 7)
        ws.set_column(4, 4, 20)
        ws.set_column(5, 5, 10)

        #header
        ws.write_string(row, col, self.classdata["name"], self.__cs({"bold": True, "font_size": "10", "align": "left"}))
        ws.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col+1),
            xl_rowcol_to_cell(row, col+2)), u'Dotazník B3', self.__cs({"bold": True, "font_size": "10", "align": "center"}))
        datestr = u"Sebráno: " + datetime.datetime.fromtimestamp(self.classdata["created"]).strftime("%d.%m.%Y")
        ws.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col+4),
            xl_rowcol_to_cell(row, col+5)), datestr, self.__cs({"bold": True, "font_size": "10", "align": "right"}))

        #Yet another header
        row = 2
        ws.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col+1),
            xl_rowcol_to_cell(row, col+2)), u'Atraktivita a neatraktivita podle voleb', self.__cs({"font_size": "10", "align": "center"}))

        ws.merge_range('{}:{}'.format(
            xl_rowcol_to_cell(row, col+4),
            xl_rowcol_to_cell(row, col+5)), u"Hierarchie třídy", self.__cs({"font_size": "10", "align": "center"}))

        attractivity_table = m.QuestionnaireModel.getQualitativeData(self.classdata["id"], order_by_hierarchy=False)
        hierarchy_table = m.QuestionnaireModel.getQualitativeData(self.classdata["id"], order_by_hierarchy=True)

        #Write positive
        row = 4
        col = 1
        inc = 0
        for line in attractivity_table:
            ws.write(row+inc, col, line["name"], self.__cs({"border": 1}))
            ws.write_number(row+inc, col+1, line["attractivity"], self.__cs({"border": 1}))
            inc += 1

        #write negative
        row = 4
        col = 4
        inc = 0
        for line in hierarchy_table:
            ws.write(row+inc, col, line["name"], self.__cs({"border": 1}))
            ws.write_number(row+inc, col+1, line["hierarchy"], self.__cs({"border": 1}))
            inc += 1
        #positive_data = m.ClassModel.getPositive

    def _writeQuantitativeTable(self):
        u"""Writes quantitative table from DB to Excel"""
        ws = self.worksheet_quantitative
        ws.set_column(0, 0, 25, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(1, 1, 3, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(2, 2, 5, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(3, 3, 1, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(4, 4, 39, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(5, 5, 6, self.__cs({"font": "Arial", "size": 10}))
        ws.set_column(6, 6, 6, self.__cs({"font": "Arial", "size": 10}))

        std_style = self.__cs({"top": 1, "bottom": 1, "font": "Arial", "size": 10})
        lalign_style = self.__cs({"top": 1, "bottom": 1, "font": "Arial", "size": 10, "align": "left"})
        ralign_style = self.__cs({"top": 1, "bottom": 1, "font": "Arial", "size": 10, "align": "right"})
        top_style = self.__cs({"top": 2, "bottom": 1, "font": "Arial", "size": 10})
        bottom_style = self.__cs({"top": 1, "bottom": 2, "font": "Arial", "size": 10})

        ######## Writing template ############
        #Header
        ws.merge_range("A1:G1", u"Tabulka B-3 kvantitativního rozboru", self.__cs({"size": 13, "bold": True, "align": "center"}))
        #initial paragraph
        ws.write_string(2, 0, u"Třída", self.__cs({"left": 2, "top": 2}))
        ws.merge_range("B3:G3", self.classdata["name"], self.__cs({"right": 2, "top": 2}))
        ws.write_string(3, 0, u"Počet žáků", self.__cs({"left": 2, "align": "left"}))
        ws.merge_range("B4:G4", "?", self.__cs({"right": 2}))
        ws.write_string(4, 0, u"Počet zúčastněných", self.__cs({"left": 2, "align": "left"}))
        ws.merge_range("B5:G5", 0, self.__cs({"right": 2, "align": "left"}))
        ws.write_string(5, 0, u"V %", self.__cs({"left": 2, "bottom": 2, "align": "left"}))
        ws.merge_range("B6:G6", "=(B5/B4)*100", self.__cs({"right": 2, "bottom": 2, "align": "left"}))

        #second paragraph
        line7 = ["", "", "", "", "", u"SUMA", u"Průměr"]
        ws.write_row(7, 0, line7, top_style)
        line8 = [u"Kladné pocity", "", "(5-35)", "",	u"Z otázky 5 - aritmetický průměr", "", ""]
        line9 = [u"Kvalita kolektivu", "", "(0-5)", "",	u"Z otázky 5 - aritmetický průměr", "", ""]
        ws.write_row(8, 0, line8, std_style)
        ws.write_row(9, 0, line9, bottom_style)
        ws.write_formula("G9", "=F9/B5", std_style)
        ws.write_formula("G10", "=F10/B5", bottom_style)

        #11
        line11 = [u"Pocit bezpečí",	"", "(1-7)", "", u"Z otázky 5 - aritmetický průměr 1. řádku"]
        line12 = [u"Pocit přátelství", "", "(1-7)", "", u"Z otázky 5 - aritmetický průměr 2. řádku"]
        line13 = [u"Atmosféra spolupráce", "", "(1-7)", "", u"Z otázky 5 - aritmetický průměr 3. řádku"]
        line14 = [u"Pocit důvěry", "", "(1-7)", "", u"Z otázky 5 - aritmetický průměr 4. řádku"]
        line15 = [u"Pocit tolerance", "", "(1-7)", "", u"Z otázky 5 - aritmetický průměr 5. řádku"]
        ws.write_row(11, 0, line11, top_style)
        ws.write_row(12, 0, line12, std_style)
        ws.write_row(13, 0, line13, std_style)
        ws.write_row(14, 0, line14, std_style)
        ws.write_row(15, 0, line15, bottom_style)
        ws.write_formula("G12", "=F12/B5", top_style)
        ws.write_formula("G13", "=F13/B5", std_style)
        ws.write_formula("G14", "=F14/B5", std_style)
        ws.write_formula("G15", "=F15/B5", std_style)
        ws.write_formula("G16", "=F16/B5", bottom_style)

        line17 = [u"Ve třídě je nešťastný žák", "", "ano", "", u"Z otázky 4 - procenta odpovědi ano"]
        line18 = [u"Ve třídě je ubližovaný žák", "", "ano", "", u"Z otázky 4 - procenta odpovědi ano"]
        line19 = [u"Do třídy se těším", "", "ano", "", u"Z otázky 4 - procenta odpovědi ano"]
        line20 = [u"Někdo mi pomůže s problémy", "", "ano", "", u"Z otázky 4 - procenta odpovědi ano"]
        line21 = [u"Problémy řešíme v klidu", "", "ano", "", u"Z otázky 4 - procenta odpovědi ano"]
        ws.write_row(17, 0, line17, top_style)
        ws.write_row(18, 0, line18, std_style)
        ws.write_row(19, 0, line19, std_style)
        ws.write_row(20, 0, line20, std_style)
        ws.write_row(21, 0, line21, bottom_style)
        ws.write_formula("G18", "=100*F18/B5", top_style)
        ws.write_formula("G19", "=100*F19/B5", std_style)
        ws.write_formula("G20", "=100*F20/B5", std_style)
        ws.write_formula("G21", "=100*F21/B5", std_style)
        ws.write_formula("G22", "=100*F22/B5", bottom_style)

        line23 = [u"Žáci v kladné polovině třídy", "", "", "", u"Z hierarchie - v % s kladným ziskem a nulou"]
        ws.write_row(23, 0, line23, self.__cs({"top": 2, "bottom": 2, "font": "Arial", "size": 10}))

        #These are tricky :-(
        ws.write(25, 0, u"Počet vzájemných voleb", top_style)
        ws.merge_range("B26:C26", u"kladných", top_style)
        ws.write(25, 3, "",  top_style)
        ws.write(25, 4, u"Ze sociogramu kladných voleb",  top_style)
        ws.merge_range("B27:C27", u"záporných", std_style)
        ws.write(26, 3, u"", std_style)
        ws.write(26, 4, u"Ze sociogramu záporných voleb", std_style)
        ws.write(27, 0, u"Index", std_style)
        ws.merge_range("B28:C28", u"kladných", std_style)
        ws.write(27, 3, u"", std_style)
        ws.write(27, 4, u"Vyděleno počtem přítomných", std_style)
        ws.write(28, 0, "", bottom_style)
        ws.merge_range("B29:C29", u"záporných", bottom_style)
        ws.write(28, 3, "", bottom_style)
        ws.write(28, 4, u"Vyděleno počtem přítomných", bottom_style)

        ws.write_formula("G28", "=G26/B5", std_style)
        ws.write_formula("G29", "=G27/B5", bottom_style)
        #For styles
        ws.write("G26", "", top_style)
        ws.write("F26", "", top_style)
        ws.write("F27", "", std_style)
        ws.write("F28", "", std_style)
        ws.write("F29", "", bottom_style)


        ws.write(30, 0, u"Počet voleb celkem", top_style)
        ws.merge_range("B31:C31", u"kladných", top_style)
        ws.write(30, 3, "", top_style)
        ws.write(30, 4, u"Ze sociogramu kladných voleb", top_style)
        ws.merge_range("B32:C32", u"záporných", std_style)
        ws.write(31, 3, u"", std_style)
        ws.write(31, 4, u"Ze sociogramu záporných voleb", std_style)
        ws.write(32, 0, u"Index", std_style)
        ws.merge_range("B33:C33", u"kladných", std_style)
        ws.write(32, 3, u"", std_style)
        ws.write(32, 4, u"Vyděleno počtem přítomných", std_style)
        ws.write(33, 0, "", self.__cs({"bottom": 2, "font": "Arial", "size": 10}))
        ws.merge_range("B34:C34", u"záporných", self.__cs({"bottom": 2, "font": "Arial", "size": 10}))
        ws.write(33, 3, "", self.__cs({"bottom": 2, "font": "Arial", "size": 10}))
        ws.write(33, 4, u"Vyděleno počtem přítomných", self.__cs({"bottom": 2, "font": "Arial", "size": 10}))
        #For styles
        ws.write("F31", "", top_style)
        ws.write("F32", "", std_style)
        ws.write("F33", "", std_style)
        ws.write("F34", "", bottom_style)
        ws.write_formula("G33", "=G31/B5", std_style)
        ws.write_formula("G34", "=G32/B5", bottom_style)

        #Yet another different cell merging
        line35 = [u"Index pozitivity", "", "", "", u"suma kladných vlastností"]
        ws.write_row(35, 0, line35, self.__cs({"top": 2, "bottom": 1, "font": "Arial", "size": 10}))
        line36 = [u"", "", "", "", u"suma záporných znalostí"]
        ws.write_row(36, 0, line36, std_style)
        ws.write(37, 0, "", std_style)
        ws.merge_range("B38:E38", u"index = suma kladných/suma záporných*100", std_style)
        ws.write_formula("G38", "=G36/G37*100", std_style)
        #For styles
        ws.write("F36", "", top_style)
        ws.write("F37", "", std_style)
        ws.write("F38", "", std_style)
        ws.write("F39", "", std_style)
        ws.write("F40", "", std_style)
        ws.write("F41", "", std_style)
        ws.write("F42", "", bottom_style)



        ws.write_row(38, 0, ["", "", "", "", "", "", ""], std_style)
        line39 = [u"Index sociálního klimatu", "", "", "", u"suma kladných bodů"]
        ws.write_row(39, 0, line39, std_style)
        line40 = [u"", "", "", "", u"suma záporných bodů"]
        ws.write_row(40, 0, line40, std_style)
        ws.write(41, 0, "", self.__cs({"top": 1, "bottom": 2, "font": "Arial", "size": 10}))
        ws.merge_range("B42:E42", u"index = suma kladných/suma záporných*100", self.__cs({"top": 1, "bottom": 2, "font": "Arial", "size": 10}))
        #For styles
        ws.write("G40", "", std_style)
        ws.write("G41", "", std_style)
        ws.write_formula("G42", "=G40/G41*100", bottom_style)

        line43 = [u"Míra empatie", "", "", "", u"počet neempatických žáků"]
        line44 = ["", "", "", "", u"index = neempat.ž./počet žáků"]
        ws.write_row(43, 0, line43, self.__cs({"top": 2, "bottom": 1, "font": "Arial", "size": 10}))
        ws.write_row(44, 0, line44, self.__cs({"top": 1, "bottom": 2, "font": "Arial", "size": 10}))
        ws.write_formula("G45", "=G44/B5", bottom_style)
        #For styles
        ws.write("F44", "", top_style)
        ws.write("F45", "", bottom_style)

        ###### Write formulas ######
        #TODO: write here the know how
        data = m.QuestionnaireModel.getQuantitativeData(self.classdata["id"])
        #First paragraph
        ws.write("B4", data["children_count"], lalign_style)
        ws.write("B5", data["children_count"]-data["missing"], lalign_style)
        #second paragraph
        ws.write("F9", data["positive_feelings"], std_style)
        ws.write("F10", data["quality"], bottom_style)
        #third paragraph
        ws.write("F12", data["scale1"], top_style)
        ws.write("F13", data["scale2"], std_style)
        ws.write("F14", data["scale3"], std_style)
        ws.write("F15", data["scale4"], std_style)
        ws.write("F16", data["scale5"], bottom_style)
        ws.write_formula("G12", "=F12/B5", top_style)
        ws.write_formula("G13", "=F13/B5", std_style)
        ws.write_formula("G14", "=F14/B5", std_style)
        ws.write_formula("G15", "=F15/B5", std_style)
        ws.write_formula("G16", "=F16/B5", bottom_style)
        #fourth paragraph
        ws.write("F18", data["yesnoquest1"], top_style)
        ws.write("F19", data["yesnoquest2"], std_style)
        ws.write("F20", data["yesnoquest3"], std_style)
        ws.write("F21", data["yesnoquest4"], std_style)
        ws.write("F22", data["yesnoquest5"], bottom_style)
        ws.write_formula("G18", "=F18/B5*100", top_style)
        ws.write_formula("G19", "=F19/B5*100", std_style)
        ws.write_formula("G20", "=F20/B5*100", std_style)
        ws.write_formula("G21", "=F21/B5*100", std_style)
        ws.write_formula("G22", "=F22/B5*100", bottom_style)
        #fifth
        ws.write("F24", u'=(COUNTIF(Kvalitativní!F5:F115,">=0")', self.__cs({"top": 2, "bottom": 2, "font": "Arial", "size": 10}))
        ws.write("G24", u'=(COUNTIF(Kvalitativní!F5:F115,">=0")/B4)*100', self.__cs({"top": 2, "bottom": 2, "font": "Arial", "size": 10}))
        #sixth
        ws.write("G26", data["bidirectional_friends"], top_style)
        ws.write("G27", data["bidirectional_antipathys"], std_style)
        #seventh
        ws.write("G31", data["friend_all"], top_style)
        ws.write("G32", data["antipathy_all"], std_style)
        #eighth
        ws.write("G36", data["traits_positive"], top_style)
        ws.write("G37", data["traits_negative"], std_style)
        ws.write("G40", u'=SUM(Přehled!T4:T'+str(4+data["children_count"])+')', std_style)
        ws.write("G41", u'=SUM(Přehled!U4:U'+str(4+data["children_count"])+')', std_style)
        #ninth paragraph
        ws.write("G44", data["empathy"], top_style)


    @staticmethod
    def makeSafeFilename(inputstr):
        u"""Takes filename and makes it safe for dumb filesystems. Adds zero if name is short"""
        keepcharacters = (' ', '.', '_')
        proposed_name = "".join(c for c in inputstr if c.isalnum() or c in keepcharacters).rstrip()
        if len(proposed_name) < 2:
            proposed_name += "0"
        return proposed_name

    def export(self):
        u"""Creates and fills XLSX file for exported class"""
        self._writeOverviewTable()
        self._writeQuantitativeTable()
        self._writeSociometryTable()
        self._writeQualitativeTable()
        self._finish()
        return self.file.getvalue()
