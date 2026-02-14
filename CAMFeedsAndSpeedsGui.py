# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the Feeds & Speeds addon.

# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import os
import re

from PySide import QtGui

import FreeCAD
import FreeCADGui
import Path
from importFCMat import read
import MaterialEditor

import CAMFeedsAndSpeeds

dir = os.path.dirname(__file__)
ui_name = "CAMFeedsAndSpeedsGui.ui"
path_to_ui = os.path.join(dir, ui_name)
material_dir = os.path.join(dir, 'Materials')
iconPath = os.path.join(dir, 'Icons')
prefs = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Material/Resources")

class FeedSpeedPanel():
    def __init__(self):
        # Build GUI
        self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)

        self.customMaterialDir = "" # store the original custom materials directory
        self.materials = [] # materials loaded from FreeCAD Materials
        self.material = {}  # selected material

        # Init
        self.calculation = CAMFeedsAndSpeeds.FSCalculation()
        self.load_materials()
        self.setup_ui()
        self.calculate()

        # connect
        self.form.material_CB.currentIndexChanged.connect(self.set_material)
        self.form.hss_RB.toggled.connect(self.set_tool_material)
        self.form.cbd_RB.toggled.connect(self.set_tool_material)
        self.form.flutes_SB.valueChanged.connect(self.calculate)
        self.form.FPT_SB.valueChanged.connect(self.calculate)
        self.form.WOC_SP.textChanged.connect(self.calculate)
        self.form.DOC_SP.textChanged.connect(self.calculate)
        self.form.ss_LE.textChanged.connect(self.calculate)
        self.form.rpm_LE.textChanged.connect(self.calculate)
        self.form.toolController_CB.currentIndexChanged.connect(self.load_tool_properties)
        self.form.update_PB.clicked.connect(self.update_tool_controller)
        self.form.close_PB.clicked.connect(self.quit)
        self.form.material_editor_PB.clicked.connect(self.show_material_editor)

    def setup_ui(self):
        """setup the user interface"""
        # load widget data
        self.load_material_combobox()
        self.set_tool_properties()
        self.form.material_editor_PB.setIcon(QtGui.QIcon(os.path.join(iconPath, "Material.svg")))

        # set input validation
        self.onlyInt = QtGui.QIntValidator()
        self.onlyInt.setBottom(1)
        self.form.ss_LE.setValidator(self.onlyInt)
        self.form.rpm_LE.setValidator(self.onlyInt)

        self.form.WOC_SP.setProperty("minimum", 0.0)
        self.form.DOC_SP.setProperty("minimum", 0.0)

        self.load_tools()
        self.load_tool_properties()
        self.set_tool_material()
        self.set_material()
    
    def load_materials(self):
        """load all materials that contain the required properties"""
        for file in os.listdir(material_dir):
            if file.endswith(".FCMat"):
                material_card = read(os.path.join(material_dir, file))
                if self.is_path_material(material_card):
                    self.materials.append(material_card)
        # sort the material list alphabetically
        self.materials = sorted(self.materials, key=lambda d: d['Name']) 

    def load_material_combobox(self):
        """display materials on the form"""
        self.form.material_CB.clear()
        for material in (d['Name'] for d in self.materials):
            self.form.material_CB.addItem(material)

    def show_material_editor(self):
        """load the FreeCAD material editor"""
        new_material = MaterialEditor.editMaterial(material=self.material)

        if new_material:
            if self.is_path_material(new_material):
                # clear all materials and load just the new material
                self.materials = []
                self.materials.append(new_material)
                self.load_material_combobox()
            else:
                QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), "Warning", "Material is missing path parameters")

    def set_tool_properties(self, dia=6, flutes=2, chipload=None, material="HSS"):
        # print("dia", dia)
        # print("flutes", flutes)
        # print("chipload", chipload)
        # print("material", material)
        """set the tool properties for the selected tool"""
        self.form.toolDia_LE.setText(str(dia))
        self.form.flutes_SB.setValue(flutes)

        if chipload is None or chipload == 0:
            chipload = dia * 0.005
        self.form.FPT_SB.setValue(chipload)

        self.form.WOC_SP.setText(str(round(dia * 0.2, 2)))
        self.form.WOC_SP.setProperty("maximum", float(dia))
        self.form.DOC_SP.setText(str(dia))

        if material == "HSS":
            self.form.hss_RB.setChecked(True)
        elif material == "Carbide":
            self.form.cbd_RB.setChecked(True)
    
    def is_path_material(self, material_card):
        """check the material contains the path properties"""
        #TODO: Add additional props
        if 'SurfaceSpeed_HSS' in material_card:
            return True
        
        return False

    def set_material(self):
        """set the material properties"""
        if len(self.materials) and self.form.material_CB.count():
            self.material = self.materials[self.form.material_CB.currentIndex()]
            self.calculation.set_material(self.material)
            self.set_surface_speed()
            self.calculate()

    def set_surface_speed(self):
        """set the surface speed for the selected material and tool"""
        ss = self.material.get("SurfaceSpeed_" + self.tool_material)
        self.form.ss_LE.setText(str(ss))
        
    def set_tool_material(self):
        """set the tool material"""
        self.tool_material = "HSS" if self.form.hss_RB.isChecked() else "Carbide"
        self.set_surface_speed()
        self.calculate()

    def load_tools(self):
        """load the tools for all jobs in the current document"""
        jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
        for job in jobs:
            for idx, tc in enumerate(job.Tools.Group):
                self.form.toolController_CB.addItem(tc.Label)

    def load_tool_properties(self):
        """load the properties from the selected tool"""
        tc = self.get_tool_controller()

        if tc:
            tool = tc.Tool
            dia = tool.Diameter
            # Hacky way to check for legacy tools, remove this after the release of 0.21
            # if not hasattr(tool, "BitShape"):
            #     FreeCAD.Console.PrintError("Legacy Tools Not Supported: " + tool.Name + "\n")
            #     self.set_tool_properties(dia)
            #     return
            flutes = tool.Flutes
            material = tool.Material
            chipload = tool.Chipload
            self.set_tool_properties(dia, flutes, chipload, material)

    def get_tool_controller(self):
        """get the tool controller"""
        jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
        tcStr = self.form.toolController_CB.currentText()
        for job in jobs:
            for tc in job.Tools.Group:
                if tc.Label == tcStr:
                    return tc

        return None

    def update_tool_controller(self):
        """write the calculated parameters to the selected tool controller"""
        tc = self.get_tool_controller()

        if tc:
            rpm = re.sub("[^0-9.]", "", self.form.rpm_result.text())
            hfeed = self.form.hfeed_result.text()
            vfeed = self.form.vfeed_result.text()
            # TODO: Add a confirmation dialog
            tc.HorizFeed = hfeed
            tc.VertFeed = vfeed
            tc.SpindleSpeed = float(rpm)

    def validate_input(self):
        """ validate the user input"""
        if self.form.WOC_SP.text() == "":
            return False
        
        if self.form.DOC_SP.text() == "":
            return False

        if self.form.ss_LE.text() == "":
            return False

        return True

    def calculate(self):
        """perform the feeds and speeds calculation"""
        if self.calculation.material is None:
            return

        if not self.validate_input():
            return

        tool = CAMFeedsAndSpeeds.Tool()

        self.calculation.rpm_overide = self.form.rpm_LE.text()
        surfaceSpeed = float(self.form.ss_LE.text())

        if not self.form.rpm_LE.text() == "":
            self.form.rpm_result.setEnabled(False)
        else:
            self.form.rpm_result.setEnabled(True)

        tool.toolDia = FreeCAD.Units.Quantity(self.form.toolDia_LE.text())
        tool.flutes = self.form.flutes_SB.value()
        self.calculation.feedPerTooth = float(self.form.FPT_SB.value())
        self.calculation.WOC = FreeCAD.Units.Quantity(self.form.WOC_SP.text())
        self.calculation.DOC = FreeCAD.Units.Quantity(self.form.DOC_SP.text())
        self.calculation.toolWear = 1.1  # Tool Wear pg: 1048

        if not self.calculation.feedPerTooth:
            return

        rpm, hfeed, vfeed, Hp = self.calculation.calculate(tool, surfaceSpeed)

        self.form.rpm_result.setText(str(rpm))
        self.form.rpm_result.setText(str(rpm) + " rpm")
        self.form.hfeed_result.setText(str(hfeed) + " mm/min")
        self.form.vfeed_result.setText(str(vfeed) + " mm/min")
        self.form.hp_result.setText("-")
        if Hp is not None:
            watts = Hp * 745.69
            self.form.hp_result.setText(str(round(Hp, 2)) + " hp / " + str(round(watts, 3)) + " watts")

    def show(self):
        """show the form"""
        # get the current custom materials directory
        self.customMaterialDir = prefs.GetString("CustomMaterialsDir", "")
        # set the custom materials directory to the supplied materials directory
        prefs.SetString("CustomMaterialsDir", material_dir)
        # show the form using the builtin exec_() function
        self.form.exec_()

    def reject(self):
        """handle reject calls"""
        FreeCAD.Console.PrintMessage("Reject Signal")
        self.quit()

    def accept(self):
        """handle accept calls"""
        self.quit()

    def quit(self):
        """handle quit calls, close the form"""
        # restore the custom materials directory
        prefs.SetString("CustomMaterialsDir", self.customMaterialDir)
        self.form.close()

    def reset(self):
        """handle reset calls"""
        pass


def Show():
    """ show the speeds and feeds dialog"""
    if not FreeCAD.ActiveDocument:
        QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), "Warning", "No Active Document")
        return

    jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
    if len(jobs) == 0:
        QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), "Warning", "No Path Job in Current Document")
        return

    # create a FeedSpeedPanel form object
    panel = FeedSpeedPanel()
    # Show the form
    panel.show()
