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
        self.tabWidget = self.form.tabWidget
        self.material_CB = self.form.material_CB
        self.hss_RB = self.form.hss_RB
        self.cbd_RB = self.form.cbd_RB
        #####################################
        ##           Milling Page          ##
        #####################################
        self.toolDia_LE = self.form.toolDia_LE
        self.flutes_SB = self.form.flutes_SB
        self.FPT_SB = self.form.FPT_SB
        self.WOC_SP = self.form.WOC_SP
        self.DOC_SP = self.form.DOC_SP
        #####################################
        ##           Drilling Page         ##
        #####################################
        self.drillDia_LE = self.form.drillDia_LE
        self.drillFPT_SB = self.form.drillFPT_SB
        self.drilling_notes = self.form.drilling_notes
        #####################################
        ##             Results             ##
        #####################################
        self.rpm_result = self.form.rpm_result
        self.rpm_LE = self.form.rpm_LE
        self.feed_result= self.form.feed_result
        self.hp_result = self.form.hp_result
        ### Set Defaults
        self.toolDia = 6
        ### Init 
        self.setup_ui()
        self.calculate()

        ### connect
        self.tabWidget.currentChanged.connect(self.calculate)
        self.material_CB.currentIndexChanged.connect(self.calculate)
        self.hss_RB.toggled.connect(self.calculate)
        self.cbd_RB.toggled.connect(self.calculate)
        self.toolDia_LE.textChanged.connect(self.calculate)
        self.flutes_SB.valueChanged.connect(self.calculate)
        self.FPT_SB.valueChanged.connect(self.calculate)
        self.WOC_SP.textChanged.connect(self.calculate)
        self.DOC_SP.textChanged.connect(self.calculate)
        self.rpm_LE.textChanged.connect(self.calculate)
        self.drillDia_LE.textChanged.connect(self.calculate)
        self.drillFPT_SB.valueChanged.connect(self.calculate)

    def setup_ui(self):    
    
        ### load materials
        materials = PathFeedsAndSpeeds.load_materials()
        for material in (d['material'] for d in PathFeedsAndSpeeds.load_materials()):
            self.material_CB.addItem(material)

        ### set tool material
        self.hss_RB.setChecked(True)    

        ### load widget data
        self.toolDia_LE.setText(str(self.toolDia))
        self.flutes_SB.setValue(2)
        self.FPT_SB.setValue(self.toolDia * 0.01)  
        self.WOC_SP.setText(str(round(self.toolDia * 0.2, 2)))
        self.DOC_SP.setText(str(self.toolDia))
        self.drillDia_LE.setText(str(self.toolDia))
        self.drillFPT_SB.setValue(self.toolDia * 0.01)

    def calculate(self):
        tool = PathFeedsAndSpeeds.Tool()
        calculation = PathFeedsAndSpeeds.FSCalculation()
        calculation.material = self.material_CB.currentText()
        calculation.rpm_overide = self.rpm_LE.text()

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

        if not calculation.feedPerTooth:
            return

        rpm, feed, Hp = calculation.calculate(tool)

        self.rpm_result.setText(str(rpm))
        self.feed_result.setText(str(feed) + " mm/min")
        self.hp_result.setText(str(round(Hp, 2)) + " hp")

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






