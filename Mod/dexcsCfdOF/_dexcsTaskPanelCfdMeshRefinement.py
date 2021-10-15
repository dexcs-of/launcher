# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2016 - Bernd Hahnebach <bernd@bimstatik.org>            *
# *   Copyright (c) 2017 Johan Heyns (CSIR) <jheyns@csir.co.za>             *
# *   Copyright (c) 2017 Oliver Oxtoby (CSIR) <ooxtoby@csir.co.za>          *
# *   Copyright (c) 2017 Alfred Bogaers (CSIR) <abogaers@csir.co.za>        *
# *   Copyright (c) 2019-2020 Oliver Oxtoby <oliveroxtoby@gmail.com>        *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD
import FreeCADGui
from PySide import QtGui
import os
import dexcsCfdTools
from dexcsCfdTools import getQuantity, setQuantity
import dexcsCfdFaceSelectWidget
from FreeCAD import Units
import re
import pythonVerCheck

# import sys
# import gettext

# localedir = os.path.expanduser("~") + "/.FreeCAD/Mod/dexcsCfdOF/locale"
# if sys.version_info.major == 3:
# 	gettext.install("dexcsCfMeshSetting", localedir)
# else:
# 	gettext.install("dexcsCfMeshSetting", localedir, unicode=True)


class _TaskPanelCfdMeshRefinement:
    """ The TaskPanel for editing References property of MeshRefinement objects """

    def __init__(self, obj):
        FreeCADGui.Selection.clearSelection()
        self.sel_server = None
        self.obj = obj
        self.mesh_obj = self.getMeshObject()

        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.join(os.path.dirname(__file__), "dexcsTaskPanelCfdMeshRefinement.ui"))

        self.form.setWindowTitle(_("Mesh refinement"))
        self.form.surfaceRefinementToggle.setText(_("Surface"))
        self.form.volumeRefinementToggle.setText(_("Internal Volume"))
        self.form.label_7.setText(_("Cartesian Mesh: Type of Refinement"))
        self.form.label_cellsize.setText(_("Real cell size:"))
        self.form.label_reflevel.setText(_("Refinement level:"))
        self.form.label_11.setText(_("Boundary Layers"))
        self.form.label_12.setText(_("More Option"))
        self.form.label_expratio.setText(_("Expansion ratio:"))
        self.form.label_firstlayerheight.setText(_("max 1st cell height:"))
        self.form.check_allowdiscont.setText(_("allowDiscontinuity"))
        self.form.label_numlayer.setText(_("number of layers:"))
        self.form.label_refinethick.setText(_("Refinement thickness:"))
        self.form.check_keepCells.setText(_("keepCellsIntersectingPatches"))
        self.form.label_4.setText(_("Objects"))
        self.form.label.setText(_("Objects"))


        self.ReferencesOrig = list(self.obj.References)

        # Face list selection panel - modifies obj.References passed to it
        self.faceSelector = dexcsCfdFaceSelectWidget.CfdFaceSelectWidget(self.form.referenceSelectWidget,
                                                                    self.obj, True, False,
                                                                    self.mesh_obj.MeshUtility == 'gmsh',
                                                                    self.mesh_obj.MeshUtility == 'gmsh')

        self.solidSelector = dexcsCfdFaceSelectWidget.CfdFaceSelectWidget(self.form.volReferenceSelectWidget,
                                                                     self.obj,
                                                                     False,
                                                                     True)

        self.form.check_boundlayer.stateChanged.connect(self.updateUI)
        self.form.check_moreoption.stateChanged.connect(self.updateUI)

        #tool_tip_mes = "Cell size relative to base cell size"
        tool_tip_mes = _("Cell size for Reference objects")
        self.form.if_cellsize.setToolTip(tool_tip_mes)
        self.form.label_cellsize.setToolTip(tool_tip_mes)

        tool_tip_mes = _("Refinement Level for Reference objects")
        self.form.if_reflevel.setToolTip(tool_tip_mes)
        self.form.label_reflevel.setToolTip(tool_tip_mes)

        self.baseMeshSize = Units.Quantity(self.mesh_obj.BaseCellSize).Value
        #print('baseMeshSize = ' + str(self.baseMeshSize))
        if self.obj.CellSize == 0 :
             self.obj.CellSize = self.baseMeshSize * 0.5


        self.load()

        self.form.if_reflevel.valueChanged.connect(self.changeCellSize)
        self.form.if_cellsize.valueChanged.connect(self.changeBaseCellSize)



        self.form.surfaceRefinementToggle.toggled.connect(self.changeInternal)
        self.form.volumeRefinementToggle.toggled.connect(self.changeInternal)

        self.form.if_refinethick.setToolTip(_("Distance the refinement region extends from the reference "
                                            "surface"))
        self.form.if_numlayer.setToolTip(_("Number of boundary layers if the reference surface is an external or "
                                         "mesh patch"))
        self.form.if_expratio.setToolTip(_("Expansion ratio of boundary layers (limited to be greater than 1.0 and "
                                         "smaller than 1.2)"))
        self.form.if_firstlayerheight.setToolTip(_("Maximum first cell height (ignored if set to 0.0)"))
        #self.form.if_edgerefinement.setToolTip("Number of edge or feature refinement levels")

        self.updateUI()

    def changeBaseCellSize(self):
        #print('refLevel clicked' )
        cellLength = getQuantity(self.form.if_cellsize)
        cellLength = re.findall("\d+\.\d+", str(cellLength))[0]
        #LengthMax = LengthMax  * 2**(self.form.if_reflevel.value())

        #print('refLevel = ' + str(cellLength))

        #LengthMax = 0.3
        self.mesh_obj.BaseCellSize = float(cellLength) * 2**(self.form.if_reflevel.value())
        return True

    def changeCellSize(self):

        #print('refLevel = ')
        #print('refLevel = ' + str(self.form.if_reflevel.value()))
        
        setQuantity(self.form.if_cellsize, self.baseMeshSize/2**(self.form.if_reflevel.value()))
        return True

    def accept(self):
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        # Macro script


        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.CellSize "
                             "= '{}'".format(self.obj.Name, getQuantity(self.form.if_cellsize)))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.RefinementLevel "
                             "= {}".format(self.obj.Name, self.form.if_reflevel.value()))

        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.KeepCell "
                             "= {}".format(self.obj.Name, self.form.check_keepCells.isChecked()))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.RemoveCell "
                             "= {}".format(self.obj.Name, self.form.check_removeCells.isChecked()))
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.AllowDiscont "
                             "= {}".format(self.obj.Name, self.form.check_allowdiscont.isChecked()))




        if self.mesh_obj.MeshUtility != 'gmsh':
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.RefinementThickness "
                                 "= '{}'".format(self.obj.Name, getQuantity(self.form.if_refinethick)))
            if self.form.check_boundlayer.isChecked():
                num_layers = self.form.if_numlayer.value()
            else:
                num_layers = 1
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.NumberLayers "
                                 "= {}".format(self.obj.Name, num_layers))
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.ExpansionRatio "
                                 "= {}".format(self.obj.Name, self.form.if_expratio.value()))
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.FirstLayerHeight "
                                 "= '{}'".format(self.obj.Name, getQuantity(self.form.if_firstlayerheight)))
            #FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.RegionEdgeRefinement "
            #                     "= {}".format(self.obj.Name, self.form.if_edgerefinement.value()))
            FreeCADGui.doCommand("FreeCAD.ActiveDocument.{}.Internal "
                                 "= {}".format(self.obj.Name, self.form.volumeRefinementToggle.isChecked()))
        refstr = "FreeCAD.ActiveDocument.{}.References = [\n".format(self.obj.Name)
        refstr += ',\n'.join("{}".format(ref) for ref in self.obj.References)
        refstr += "]"
        FreeCADGui.doCommand(refstr)
        FreeCADGui.doCommand("FreeCAD.ActiveDocument.recompute()")
        return True

    def reject(self):
        self.obj.References = self.ReferencesOrig
        if self.sel_server:
            FreeCADGui.Selection.removeObserver(self.sel_server)
        FreeCADGui.ActiveDocument.resetEdit()

        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        return True

    def load(self):
        """ fills the widgets """
        self.form.if_reflevel.setValue(self.obj.RefinementLevel)
        setQuantity(self.form.if_cellsize, self.obj.CellSize)

        self.form.check_keepCells.setChecked(self.obj.KeepCell)
        self.form.check_removeCells.setChecked(self.obj.RemoveCell)
        self.form.check_allowdiscont.setChecked(self.obj.AllowDiscont)
        if (self.obj.KeepCell == True) or (self.obj.RemoveCell == True): 
            self.form.check_moreoption.setChecked(self.obj.KeepCell)


        if not self.mesh_obj.MeshUtility == "gmsh":
            setQuantity(self.form.if_refinethick, self.obj.RefinementThickness)
            self.form.check_boundlayer.setChecked(self.obj.NumberLayers > 1)
            self.form.if_numlayer.setValue(self.obj.NumberLayers)
            self.form.if_expratio.setValue(self.obj.ExpansionRatio)
            setQuantity(self.form.if_firstlayerheight, self.obj.FirstLayerHeight)

            #self.form.if_edgerefinement.setValue(self.obj.RegionEdgeRefinement)
            if self.obj.Internal:
                self.form.volumeRefinementToggle.toggle()

    def updateUI(self):
        self.form.surfaceOrInernalVolume.setVisible(True)
        self.form.boundlayer_frame.setVisible(self.form.check_boundlayer.isChecked())
        #self.form.moreoption_frame.setVisible(self.form.check_moreoption.isChecked())
        if self.form.check_moreoption.isChecked():
            self.form.moreoption_frame.setVisible(True)
        else:
            self.form.moreoption_frame.setVisible(False)
            self.form.check_keepCells.setChecked(False)
            self.form.check_removeCells.setChecked(False)
        if self.form.check_boundlayer.isChecked():
            if self.form.if_numlayer.value()==1:
                self.form.if_numlayer.setValue(3)
        if self.mesh_obj.MeshUtility == 'gmsh':
            self.form.cartesianInternalVolumeFrame.setVisible(False)
            self.form.cf_frame.setVisible(False)
            self.form.snappy_frame.setVisible(False)
        if self.form.volumeRefinementToggle.isChecked():
            self.form.cf_frame.setVisible(False)
            self.form.snappy_frame.setVisible(False)
            self.form.ReferencesFrame.setVisible(False)
            self.form.cartesianInternalVolumeFrame.setVisible(True)
            if self.mesh_obj.MeshUtility == 'cfMesh':
                self.form.cf_frame.setVisible(False)
            elif self.mesh_obj.MeshUtility == 'snappyHexMesh':
                self.form.snappy_frame.setVisible(True)
                self.form.snappySurfaceFrame.setVisible(False)
        else:
            self.form.ReferencesFrame.setVisible(True)
            self.form.cartesianInternalVolumeFrame.setVisible(False)
            if self.mesh_obj.MeshUtility == 'cfMesh':
                self.form.cf_frame.setVisible(True)
                self.form.snappy_frame.setVisible(False)
            elif self.mesh_obj.MeshUtility == 'snappyHexMesh':
                self.form.cf_frame.setVisible(False)
                self.form.snappy_frame.setVisible(True)
                self.form.snappySurfaceFrame.setVisible(True)

    def getMeshObject(self):
        analysis_obj = dexcsCfdTools.getActiveAnalysis()
        mesh_obj = dexcsCfdTools.getMeshObject(analysis_obj)
        if mesh_obj is None:
            message = _("Mesh object not found - please re-create.")
            QtGui.QMessageBox.critical(None, _('Missing mesh object'), message)
            doc = FreeCADGui.getDocument(self.obj.Document)
            doc.resetEdit()
        return mesh_obj

    def changeInternal(self):
        self.obj.References.clear()
        self.faceSelector.rebuildReferenceList()
        self.solidSelector.rebuildReferenceList()
        self.updateUI()
