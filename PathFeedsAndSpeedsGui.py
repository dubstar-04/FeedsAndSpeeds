# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import FreeCAD,FreeCADGui
import os
from PySide import QtGui, QtCore
from PySide.QtGui import QApplication, QDialog, QMainWindow
import PathFeedsAndSpeeds

dir = os.path.dirname(__file__)
ui_name = "PathFeedsAndSpeedsGui.ui"
path_to_ui = dir + "/" +ui_name

class FeedSpeedPanel():
    def __init__(self):
        #Build GUI
        self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)

        ### Set Defaults
        self.toolDia = 6

        ### Init
        self.calculation = PathFeedsAndSpeeds.FSCalculation()
        self.setup_ui()
        self.calculate()

        ### connect
        self.form.material_CB.currentIndexChanged.connect(self.set_surface_speed)
        self.form.hss_RB.toggled.connect(self.calculate)
        self.form.cbd_RB.toggled.connect(self.calculate)
        self.form.toolDia_LE.textChanged.connect(self.calculate)
        self.form.flutes_SB.valueChanged.connect(self.calculate)
        self.form.FPT_SB.valueChanged.connect(self.calculate)
        self.form.WOC_SP.textChanged.connect(self.calculate)
        self.form.DOC_SP.textChanged.connect(self.calculate)
        self.form.rpm_LE.textChanged.connect(self.calculate)
        self.form.toolController_CB.currentIndexChanged.connect(self.load_tool_properties)
        self.form.update_PB.clicked.connect(self.update_tool_controller)
        self.form.close_PB.clicked.connect(self.quit)

    def setup_ui(self):    
    
        ### load materials
        materials = PathFeedsAndSpeeds.load_materials()
        for material in (d['material'] for d in PathFeedsAndSpeeds.load_materials()):
            self.material_CB.addItem(material)

        ### set tool material
        self.hss_RB.setChecked(True)    

        ### load widget data

    def calculate(self):
        tool = PathFeedsAndSpeeds.Tool()
        calculation = PathFeedsAndSpeeds.FSCalculation()

        if not self.rpm_LE.text() == "":
            self.rpm_result.setEnabled(False)
        else:
            self.rpm_result.setEnabled(True)

        if self.tabWidget.currentIndex() == 0:
            # calculate for milling
            tool.toolDia = float(self.toolDia_LE.text())
            tool.flutes = self.flutes_SB.value()
            calculation.feedPerTooth = float(self.FPT_SB.value())
            calculation.WOC = FreeCAD.Units.Quantity(self.WOC_SP.text())
            calculation.DOC = FreeCAD.Units.Quantity(self.DOC_SP.text())         
            calculation.toolWear = 1.1 ## Tool Wear pg: 1048
            calculation.ss_by_material = "ss_hss" if self.hss_RB.isChecked() else "ss_cbd"
            calculation.opType = 'Milling'
        self.calculation.feedPerTooth = float(self.form.FPT_SB.value())
        self.calculation.WOC = FreeCAD.Units.Quantity(self.form.WOC_SP.text())
        self.calculation.DOC = FreeCAD.Units.Quantity(self.form.DOC_SP.text())         
        self.calculation.toolWear = 1.1 ## Tool Wear pg: 1048
        self.set_tool_material()
        self.calculation.opType = 'Milling'
        
        """         
        else:
            # calculate for drilling
            tool.toolDia = float(self.drillDia_LE.text())
            calculation.feedPerTooth = float(self.drillFPT_SB.value())
            calculation.toolWear = 1.3 ## Tool Wear pg: 1048
            calculation.ss_by_material = "ss_drill_hss" if self.hss_RB.isChecked() else "ss_drill_cbd"
            calculation.opType = 'Drilling'
            print('tooldia', tool.toolDia)
            if tool.toolDia:
                notes = 'Note: Peck drilling should be used when hole depth > {0}'
                self.drilling_notes.setText(notes.format(tool.toolDia * 4))
            else:
                self.drilling_notes.setText('') 
        """

        if not self.calculation.feedPerTooth:
            return

        rpm, feed, Hp = self.calculation.calculate(tool)

        self.form.rpm_result.setText(str(rpm))
        self.form.feed_result.setText(str(feed) + " mm/min")
        self.form.hp_result.setText(str(round(Hp, 2)) + " hp")

    def show(self):
        self.form.show()
        self.form.exec_()

    def reject(self):
        FreeCAD.Console.PrintMessage("Reject Signal")
        self.quit()

    def accept(self):
        self.quit()
        
    def quit(self):
        FreeCADGui.Control.closeDialog(self)

    def reset(self):
        pass

def Show():
    panel = FeedSpeedPanel()
    panel.show()






