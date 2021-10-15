#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FreeCAD
import Mesh
import os
import subprocess
import PySide
from PySide import QtGui
from PySide import QtCore
import dexcsCfdTools

import pythonVerCheck
import pyDexcsSwakSubset

doc = App.ActiveDocument
name = os.path.splitext(doc.FileName)[0]
modelDir = os.path.dirname(doc.FileName)

TreeFoamVersionFile = "/opt/TreeFoam/TreeFoamVersion"
#print(TreeFoamVersionFile)
if os.path.isfile(TreeFoamVersionFile) == True:
    f = open(TreeFoamVersionFile)
    TreeFoamVersion = f.read()
    f.close()

#モデルファイル置き場がケースファイルの場所（.CaseFileDictで指定）と異なる場合
caseFileDict = modelDir + "/.CaseFileDict"
if os.path.isfile(caseFileDict) == True:
    f = open(caseFileDict)
    modelDir = f.read()
    f.close()

systemFolder = modelDir + "/system"
constantFolder = modelDir + "/constant"

env = QtCore.QProcessEnvironment.systemEnvironment()

if env.contains("APPIMAGE"):
    message = (_("this FreeCAD is AppImage version.\n  some function of runParallelDialog doesen't work.\n if you want utilize the function, use normal TreeFoam menu.")) 
    ans = QtGui.QMessageBox.critical(None, _("AppImage Warning"), message, QtGui.QMessageBox.Yes)
    dexcsCfdTools.removeAppimageEnvironment(env)


if os.path.isdir(systemFolder) and os.path.isdir(constantFolder):

    CaseFilePath=modelDir
    #print(CaseFilePath)
    os.chdir(CaseFilePath)
    #geditの実行ファイル作成
    caseName = CaseFilePath
    #title =  "#!/bin/sh\n"
    title =  ""

    configDict = pyDexcsSwakSubset.readConfigTreeFoam()
    envOpenFOAMFix = configDict["bashrcFOAM"]
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    envTreeFoam = configDict["TreeFoam"]
    envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',envTreeFoam)
    envOpenFOAMFix = os.path.expanduser(envOpenFOAMFix)
    #envOpenFOAMFix = envOpenFOAMFix.replace('$TreeFoamUserPath',os.getenv("HOME")+'/.TreeFoamUser')
    #envSet = "source " + envOpenFOAMFix + '\n'
    envSet = ". " + envOpenFOAMFix + '\n'

    envSet = envSet + ". ~/.FreeCAD/runTreefoamSubset\n"
    configDict = pyDexcsSwakSubset.readConfigDexcs()
    envSwak = "export dexcsSwakPath=" + os.path.expanduser(configDict["dexcs"]) + "/SWAK\nexport PYTHONPATH=$dexcsSwakPath:$PYTHONPATH\n"
    if TreeFoamVersion.startswith('3') :
        solverSet = os.path.expanduser("~") + "/.FreeCAD/runParallelDexcs.py " + caseName
    else :
        solverSet = "runParallelDialog.py " + caseName
    sleep = ""
    cont = title + envSet + envSwak + solverSet  + sleep
    f=open("./run","w")
    f.write(cont)
    f.close()
    #実行権付与
    os.system("chmod a+x run")
    #実行
    #comm = "xfce4-terminal --execute ./run"
    #comm= "gnome-terminal --geometry=80x15 --zoom=0.9 -- bash --rcfile ./run"
    #subprocess.call(comm .strip().split(" "))
    #if TreeFoamVersion.startswith('3') :
    #    message = (_("sorry for TreeFoam Ver.3*, \n  this module cannnot activate correctly.\n You need to use this module from TreeFoam main window."))
    #    msgBox = QtGui.QMessageBox()
    #    msgBox.setWindowTitle(_("check TreeFoam version"))
    #    msgBox.setText(message)
    #    msgBox.setIcon(QtGui.QMessageBox.Warning)
    #    tryButton = msgBox.addButton(QtGui.QMessageBox.Ignore)
    #    abortButton = msgBox.addButton(QtGui.QMessageBox.Abort)
    #    msgBox.exec_()
    #    res = msgBox.clickedButton()
    #
    #    if res == tryButton:
    #        os.system(comm)
    #    else:
    #        stat = "CANCEL"
    #else :
    #os.system(comm)
    cmd = dexcsCfdTools.makeRunCommand('./run', modelDir, source_env=False)
    print('cmd = ', cmd)
    FreeCAD.Console.PrintMessage("Solver run command: " + ' '.join(cmd) + "\n")
    env = QtCore.QProcessEnvironment.systemEnvironment()
    print('env = ', env)
    #if env_vars:
    #    for key in env_vars:
    #        env.insert(key, env_vars[key])
    dexcsCfdTools.removeAppimageEnvironment(env)
    process = QtCore.QProcess()
    process.setProcessEnvironment(env)
    working_dir = modelDir
    if working_dir:
        process.setWorkingDirectory(working_dir)
    # if platform.system() == "Windows":
    #     # Run through a wrapper process to allow clean termination
    #     cmd = [os.path.join(FreeCAD.getHomePath(), "bin", "python.exe"),
    #            '-u',  # Prevent python from buffering stdout
    #            os.path.join(os.path.dirname(__file__), "WindowsRunWrapper.py")] + cmd
    # print("Raw command: ", cmd)
    process.start(cmd[0], cmd[1:])
    
else:
    message = (_("this folder is not case folder of OpenFOAM.\n  check current directory."))
    ans = QtGui.QMessageBox.critical(None, _("check OpenFOAM case"), message, QtGui.QMessageBox.Yes)

def dummyFunction(): # 何故かこれがないとうまく動かない      
    pass
