# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import re
import tempfile
import PySide
from PySide import QtGui

import pythonVerCheck


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

	message = _("the case file is ") + modelDir + _(".")
	message = message + _("\n To change the analysis case file, set the OutputPath property of Analysis container and then write meshCase on the dexcsTaskPanelCfdMesh,\n or click the Case button in the cfMesh setting macro and specify the change destination.")
	QtGui.QMessageBox.information(None, _("Confirmation of analysis case file"), message)

else:
    message = (_("this folder is not case folder of OpenFOAM.\n   check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

