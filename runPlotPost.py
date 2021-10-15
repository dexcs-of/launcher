#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import gettext
import PySide
from PySide import QtGui
import math

import pythonVerCheck
from dexcsCfdPostPlot import PostPlot
from collections import OrderedDict
import dexcsPlotPost

doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)

#モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
caseFileDict = modelDir + "/.CaseFileDict"
if os.path.isfile(caseFileDict) == True:
    f = open(caseFileDict)
    modelDir = f.read()
    f.close()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

    (fileName, selectedFilter) = QtGui.QFileDialog.getOpenFileName( None,
         _("Select a postProcess file"),modelDir + "/system" , filter="dexcs plot Files (*.dplt)")

    name = os.path.splitext(fileName)[0]

    if name != "":


        f = open(fileName,"r")
        lines = f.readlines()
        f.close()
        print("postProcessing=",f.name)

        dexcsPlotPost.dexcsPlotPost(modelDir,lines)
        #dexcsPlot.dexcs_plot(modelDir,lines)


    else:
        message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
        ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

