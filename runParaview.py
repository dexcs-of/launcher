#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools

import pythonVerCheck
import pyDexcsSwakSubset

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

    CaseFilePath=modelDir
    #print(CaseFilePath)
    os.chdir(CaseFilePath)
    #geditの実行ファイル作成
    caseName = CaseFilePath
    configDict = pyDexcsSwakSubset.readConfigTreeFoam()
    paraFoamFix = configDict["paraFoam"]
    #paraFoamFix = os.path.expanduser("~") + "/.TreeFoamUser/app/runParaFoam-DEXCS"
    title =  "#!/bin/bash\n"
    envSet = ". " + os.path.expanduser("~") + "/.FreeCAD/runTreefoamSubset\n"
    solverSet = "runParaFoamOptionDialog.py " + paraFoamFix + " " + caseName
    sleep = ""
    cont = title + envSet + solverSet + sleep
    #print(cont)
    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")
    #実行
    cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
    print('cmd = ', cmd)
    FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
    env = QtCore.QProcessEnvironment.systemEnvironment()
    print('env = ', env)
    dexcsCfdTools.removeAppimageEnvironment(env)
    process = QtCore.QProcess()
    process.setProcessEnvironment(env)
    working_dir = modelDir
    if working_dir:
        process.setWorkingDirectory(working_dir)
    process.start(cmd[0], cmd[1:])

else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
