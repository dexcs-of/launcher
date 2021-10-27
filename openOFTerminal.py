#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import subprocess
import glob
import PySide
from PySide import QtGui
import re
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

os.chdir(modelDir)


systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

        #os.system(solver)
        caseName = modelDir
        title =  "#!/bin/bash\n"

        prefs = dexcsCfdTools.getPreferencesLocation()
        installation_path = FreeCAD.ParamGet(prefs).GetString("InstallationPath", "")
        envOpenFOAMFix = os.path.expanduser(installation_path)
        envSet = "source " + envOpenFOAMFix + '/etc/bashrc\n'

        cont = title + envSet 
        f=open("./run","w")
        f.write(cont)
        f.close()
        #実行権付与
        os.system("chmod a+x run")
        #実行
        #cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
        cmd = dexcsCfdTools.makeRunCommand('gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run', modelDir, source_env=False)
        FreeCAD.Console.PrintMessage("Open Terminal for OpenFOAM: " + ' '.join(cmd) + "\n")
        env = QtCore.QProcessEnvironment.systemEnvironment()
        dexcsCfdTools.removeAppimageEnvironment(env)
        process = QtCore.QProcess()
        process.setProcessEnvironment(env)
        working_dir = modelDir
        if working_dir:
            process.setWorkingDirectory(working_dir)
        process.start(cmd[0], cmd[1:])

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass


