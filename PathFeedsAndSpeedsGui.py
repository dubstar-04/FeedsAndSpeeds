# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path


#VERY SOON LOOK INTO DETECT IF FC PRESENT...RUN/INSTALL ....
# change title from "Path feeds..." to just "Feeds & ..."???

#Cutting strategy        PRIMARY VAR(s)
#milling-15%             ss (feed)
#milling-30%             ss (feed)              chipload is a primary??? review calc chart and revise all these!!!!!
#milling-50%             ss (feed)
#milling-75%             ss (feed)
#milling-100%            ss (feed)
#woc-full                StepOver (WOC)
#roughing-medium         ss (feed) & StepOver/Down (WOC/DOC) & ??????
#roughing-aggressive     ss (feed) & StepOver/Down (WOC/DOC) & ??????
#finishing-medium        ss (feed) & StepOver/Down (WOC/DOC) & ??????
#finishing-fine          ?? ss/rpm/????
#engraving               ?? ss/rpm/????  <<<FS calc not cfg for this???

#Save cfg AND CUTTING OUTCOME!!!
#...later plot ....hmmm material/strategy    ool d/more vars/vibration/finish/....

#TC becomes a Tool UID????

#Need user setting for above & CNC limits & tools....

#app_mode_FCaddon = True    # run as FreeCAD addon
#app_mode_FCaddon = False   # run standalone without FreeCAD

import os
import sys

from PySide2 import QtGui

global app_mode_FCaddon

# Determine whether running as standalone app (except) or as FC addon.
try:
    # next line fails if this module NOT called by another module ie from FC workbench load of F&S InitGui.py
    sys._getframe(1)
    #print(sys._getframe(1)) 
    app_mode_FCaddon = True
    import FreeCAD, FreeCADGui
    import InitFeedsAndSpeeds
    ui_name = "PathFeedsAndSpeedsGui_FC.ui"
except:
    # Not called, running this module direct, so setup/run as standalone app
    app_mode_FCaddon = False
    ui_name = "PathFeedsAndSpeedsGui_Standalone.ui"

    from PyQt5.QtWidgets import (

        QApplication, QDialog, QMainWindow, QMessageBox, QWidget

    )

    from PyQt5.uic import loadUi
    #------------------------

    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, QIODevice
#------------------------


import PathFeedsAndSpeeds
dir = os.path.dirname(__file__)
path_to_ui = dir + "/" + ui_name
print(path_to_ui)

class FeedSpeedPanel():
    def __init__(self):
        # Build GUI
        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)
            #loadUi(ui_name, self)
        else:
            try: 
                ui_file_name = 'PathFeedsAndSpeedsGui_Standalone.ui'
                ui_file = QFile(ui_name)
                if not ui_file.open(QIODevice.ReadOnly):
                    print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
                    sys.exit(-1)
                loader = QUiLoader()
                self.form = loader.load(ui_file, None)
                ui_file.close()
            except Exception as err:
                    print(" 'FeedSpeedPanel' Failed. "
                                        "{err}\n".format(err=str(err)))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)

        # Set Defaults
        self.toolDia = 6

        # Init
        self.calculation = PathFeedsAndSpeeds.FSCalculation()
        self.setup_ui()
        self.calculate()

        # connect
        self.form.material_CB.currentIndexChanged.connect(self.set_material)
        self.form.hss_RB.toggled.connect(self.calculate)
        self.form.cbd_RB.toggled.connect(self.calculate)
        self.form.toolDia_LE.textChanged.connect(self.calculate)
        self.form.flutes_SB.valueChanged.connect(self.calculate)
        self.form.FPT_SB.valueChanged.connect(self.calculate)
        self.form.WOC_SP.textChanged.connect(self.calculate)
        self.form.DOC_SP.textChanged.connect(self.calculate)
        self.form.ss_LE.textChanged.connect(self.calculate)
        self.form.rpm_LE.textChanged.connect(self.calculate)
        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            self.form.toolController_CB.currentIndexChanged.connect(self.load_tool_properties)
            self.form.update_PB.clicked.connect(self.update_tool_controller)
        self.form.close_PB.clicked.connect(self.quit)

    def setup_ui(self):
        # load materials
        # materials = PathFeedsAndSpeeds.load_materials()
        for material in (d['material'] for d in PathFeedsAndSpeeds.load_materials()):
            self.form.material_CB.addItem(material)

        # load widget data
        self.set_tool_properties(self.toolDia, 2, self.toolDia * 0.01, "HSS")

        # set input validation
        self.onlyInt = QtGui.QIntValidator()
        self.form.ss_LE.setValidator(self.onlyInt)
        self.form.rpm_LE.setValidator(self.onlyInt)

        if app_mode_FCaddon:
            self.load_tools()
            self.load_tool_properties()
        self.set_tool_material()
        self.set_material()
        

    def set_tool_properties(self, dia, flutes, chipload, material):
        self.form.toolDia_LE.setText(str(dia))
        self.form.flutes_SB.setValue(flutes)
        self.form.FPT_SB.setValue(chipload)

        self.form.WOC_SP.setText(str(round(dia * 0.2, 2)))
        self.form.DOC_SP.setText(str(dia))

        if material == "HSS":
            self.form.hss_RB.setChecked(True)
        elif material == "Carbide":
            self.form.cbd_RB.setChecked(True)

    def set_material(self):
        material = self.form.material_CB.currentText()
        self.calculation.set_material(material)
        ss = self.calculation.get_surface_speed()
        self.form.ss_LE.setText(str(ss))
        
        currentTool = PathFeedsAndSpeeds.Tool()
        if app_mode_FCaddon:
            currentTool.toolDia = FreeCAD.Units.Quantity(self.form.toolDia_LE.text())
            currentTool.flutes = FreeCAD.Units.Quantity(self.form.flutes_SB.text())
        else:
            currentTool.toolDia = float(self.form.toolDia_LE.text())
            currentTool.flutes = int(self.form.flutes_SB.text())
        currentTool.material = "HSS" if self.form.hss_RB.isChecked() else "Carbide"
        #print(currentTool.toolDia, currentTool.flutes, currentTool.material)
        cl = self.calculation.get_chipload(currentTool)
        # FIXME temp cludge to **TRYING TO** ie NOT FIXED YET cope with none value of cl if cl not found!
        print ('chipload: ', cl)
        if cl:
            self.form.FPT_SB.setValue(cl)   #TODO hopefully just need cl value 
        else:
            self.form.FPT_SB.setValue(0.01)
        self.calculate

    def set_tool_material(self):
        self.calculation.ss_by_material = "ss_hss" if self.form.hss_RB.isChecked() else "ss_cbd"

    def load_tools(self):
        jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
        # self.form.toolController_CB.addItem('None')
        for job in jobs:
            for idx, tc in enumerate(job.Tools.Group):
                self.form.toolController_CB.addItem(tc.Label)

    def load_tool_properties(self):
        tc = self.get_tool_controller()

        if tc:
            tool = tc.Tool
            dia = tool.Diameter
            flutes = tool.Flutes
            material = tool.Material
            chipload = tool.Chipload
            self.set_tool_properties(dia, flutes, chipload, material)
            print("tool props:", dia, flutes, material, chipload)

    def get_tool_controller(self):
        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
            tcStr = self.form.toolController_CB.currentText()
            for job in jobs:
                for tc in job.Tools.Group:
                    if tc.Label == tcStr:
                        return tc

        return None

    def update_tool_controller(self):
        tc = self.get_tool_controller()

        if tc:
            rpm = self.form.rpm_result.text()
            hfeed = self.form.hfeed_result.text()
            vfeed = self.form.vfeed_result.text()
            # TODO: Add a confirmation dialog
            tc.HorizFeed = hfeed
            tc.VertFeed = vfeed
            tc.SpindleSpeed = float(rpm)

    def calculate(self):
        if self.calculation.material is None:
            return

        tool = PathFeedsAndSpeeds.Tool()

        self.calculation.rpm_overide = self.form.rpm_LE.text()
        surfaceSpeed = float(self.form.ss_LE.text())

        if not self.form.rpm_LE.text() == "":
            self.form.rpm_result.setEnabled(False)
        else:
            self.form.rpm_result.setEnabled(True)

        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            tool.toolDia = FreeCAD.Units.Quantity(self.form.toolDia_LE.text())
            tool.flutes = int(self.form.flutes_SB.value())
            self.calculation.feedPerTooth = float(self.form.FPT_SB.value())
            self.calculation.WOC = FreeCAD.Units.Quantity(self.form.WOC_SP.text())
            self.calculation.DOC = FreeCAD.Units.Quantity(self.form.DOC_SP.text())
        else:
            tool.toolDia = float(self.form.toolDia_LE.text())
            tool.flutes = self.form.flutes_SB.value()
            self.calculation.feedPerTooth = float(self.form.FPT_SB.value())
            self.calculation.WOC = float(self.form.WOC_SP.text())
            self.calculation.DOC = float(self.form.DOC_SP.text())

        self.calculation.toolWear = 1.1  # Tool Wear pg: 1048
        self.set_tool_material()

        if not self.calculation.feedPerTooth:
            return

        rpm, hfeed, vfeed, Hp = self.calculation.calculate(tool, surfaceSpeed)
        watts = Hp * 745.69

        self.form.rpm_result.setText(str(rpm))
        self.form.hfeed_result.setText(str(hfeed) + " mm/min")
        self.form.vfeed_result.setText(str(vfeed) + " mm/min")
        self.form.hp_result.setText(str(round(Hp, 2)) + " hp / " + str(round(watts, 2)) + " watts")
        
        # currently printing in FSCalculation.calculate
        #if app_mode_FCaddon == False:
            # For standalone print outputs to console
            #print(hfeed, vfeed, int(watts), rpm)

    def show(self):
        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            self.form.exec_()
        else:
            self.form.show()

    def reject(self):
        #if FeedsAndSpeedsConfig.app_mode_FCaddon:
        if app_mode_FCaddon:
            FreeCAD.Console.PrintMessage("Reject Signal")
        self.quit()

    def accept(self):
        self.quit()

    def quit(self):
        self.form.close()

    def reset(self):
        pass

def Show():
    if not FreeCAD.ActiveDocument:
        QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), "Warning", "No Active Document")
        return

    jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
    if len(jobs) == 0:
        QtGui.QMessageBox.warning(FreeCADGui.getMainWindow(), "Warning", "No Path Job in Current Document")
        return

    panel = FeedSpeedPanel()
    try: 
        print (panel)
        print (panel.form)
        panel.form.exec_()
        #panel.show()
    except Exception as err:
            print(" 'My function' Failed. "
                                "{err}\n".format(err=str(err)))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    
# standalone mode only
if __name__ == "__main__":
    #FeedsAndSpeedsConfig.app_mode_FCaddon = False   # run standalone without FreeCAD
    #if FeedsAndSpeedsConfig.app_mode_FCaddon == False:
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    #ATM only show FeedsAndSpeeds form, not main window .... keeps standalone vs FreeCAD code differences simpler
    #window = QWidget()
    #window.show()  # IMPORTANT!!!!! Windows are hidden by default.


    #Show()
    panel = FeedSpeedPanel()
    panel.show()

    # Start the event loop.
    #app.exec()
    sys.exit(app.exec_())
