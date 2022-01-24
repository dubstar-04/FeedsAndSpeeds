# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path



# >>>>>real data!!!!!

#gotta do updates to match all the core var names
#& poss some module name changes...
#& maybe limits

# FIXME ensure chipload etc updated AND correct calc etc values!!!!




# TODO FIXME - restore module names to more sensisble/original!!!!!

# TODO FIXME >>>REVIEW *ALL* OF THESE IN CODE!!!!!!


# TODO add cnc limit enable/disable check box to All gui's

# TODO: Re-enable drilling (vFeed & power)...have added toolType to aid this.


import os
import sys

from PySide2 import QtGui

global app_mode_FCaddon

import PathFeedsAndSpeeds
currentDir = os.path.dirname(__file__)

# get users preferences - here for the gui mode expert/detailed/whatever else added.
# using text strings as maybe possibly more than TWO gui types (as well as FC & Standalone versions of each)
prefs = PathFeedsAndSpeeds.load_user_prefs()
guiMode = next(item for item in prefs if item["pref"] == "guiModePref").get("value")

# try run as FC addon: except run as standalone app
try:
    # fails if NOT called from FC workbench load of F&S InitGui.py
    sys._getframe(1)
    # print(sys._getframe(1))
    app_mode_FCaddon = True
    import FreeCAD, FreeCADGui
    import InitFeedsAndSpeeds
    if guiMode == "expert":
        ui_name = "PathFeedsAndSpeedsGui_FC.ui"
    else:
        ui_name = "PathFeedsAndSpeedsGui_Detailed_FC.ui"
except ValueError:
    # Not called, running this module direct, so setup/run as standalone app
    app_mode_FCaddon = False
    if guiMode == "expert":
        ui_name = "PathFeedsAndSpeedsGui_Standalone.ui"
    else:
        ui_name = "PathFeedsAndSpeedsGui_Detailed_Standalone.ui"

    from PyQt5.QtWidgets import (

        QApplication, QDialog, QMainWindow, QMessageBox, QWidget

    )

    from PyQt5.uic import loadUi
    # ------------------------

    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, QIODevice
# ------------------------

path_to_ui = currentDir + "/" + ui_name
print(path_to_ui)

class FeedSpeedPanel():
    def __init__(self):
        # Build GUI
        if app_mode_FCaddon:
            self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)
            # loadUi(ui_name, self)
        else:
            try:
                #ui_file_name: str = 'PathFeedsAndSpeedsGui_Standalone.ui'
                ui_file_name: str = ui_name
                ui_file = QFile(ui_file_name)
                if not ui_file.open(QIODevice.ReadOnly):
                    print("Cannot open {}: {}"
                          .format(ui_file_name, ui_file.errorString()))
                    sys.exit(-1)
                loader = QUiLoader()
                self.form = loader.load(ui_file, None)
                ui_file.close()
            except Exception as err:
                print("FeedSpeedPanel Failed." "{err}\n".format(err=str(err)))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        # Set Defaults
        #self.toolDia = 6.0
        #self.toolName = "dflt tool"

        # Init
        self.calculation = PathFeedsAndSpeeds.FSCalculation()
        #self.calculation.tool = PathFeedsAndSpeeds.Tool()
        
        self.setup_ui()
        self.calculateUpdateGuiAndCentralVars()

        # connect
        self.form.material_CB.currentIndexChanged.connect(self.set_material)
        self.form.toolController_CB.currentIndexChanged.connect(self.load_SELECTED_tool_properties)

        # FIXME ATM user CAN change {override!!!!} and so SHOULD  
        # make each sep modle to update value in self.calculation
        # also need reconsider the override model - eg RPM handled diff to others!!
        self.form.FPT_SB.valueChanged.connect(self.calculateUpdateGuiAndCentralVars)
        self.form.WOC_SP.textChanged.connect(self.calculateUpdateGuiAndCentralVars)
        self.form.DOC_SP.textChanged.connect(self.calculateUpdateGuiAndCentralVars)
        self.form.ss_LE.textChanged.connect(self.calculateUpdateGuiAndCentralVars)
        self.form.rpm_LE.textChanged.connect(self.calculateUpdateGuiAndCentralVars)
        self.form.update_PB.clicked.connect(self.update_tool_controller_FC_ONLY)
        self.form.close_PB.clicked.connect(self.quit)


    def setup_ui(self):
        for material in (d['material'] for d in self.calculation.materials):
            self.form.material_CB.addItem(material)

        self.toolControllers = []
        if app_mode_FCaddon:
            jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
            for job in jobs:
                for tc in job.Tools.Group:
                    self.toolControllers.append(tc)
        else:
            self.toolControllers = PathFeedsAndSpeeds.load_tools_standalone_only()

        # FIXME is this required - have load_tools() etc below!!!!
        #self.set_tool_properties()

        # set input validation
        self.onlyInt = QtGui.QIntValidator()
        self.form.ss_LE.setValidator(self.onlyInt)
        self.form.rpm_LE.setValidator(self.onlyInt)

        self.load_tools()                       # Add *list* of ALL TC/Tool names/labels to gui combo box as a list
        self.load_SELECTED_tool_properties()    # Get, display(gui) & set(non-gui) TC/Tool props
        #self.set_tool_material()               # sets gui radio button BUT WHY IS THIS NOT CALLED FROM load_SELECTED_tool_properties
        self.set_material()


    def set_material(self):                     # Get selected material, UPDATE SS & CL
        material = self.form.material_CB.currentText()
        self.calculation.set_stockMaterial(material)
        
        # Changed material, so update SS, CL & CT, then re-calc outputs
        self.calculation.surfaceSpeed = self.calculation.updateSurfaceSpeed()
        self.form.ss_LE.setText(str(self.calculation.surfaceSpeed))

        self.calculation.updateChipload()
        # FIXME temp cludge **TRYING TO** ie NOT properly FIXED YET cope with none value of cl if cl not found!
        if self.calculation.chiploadForCalc == None:
            print('TEMP CLUDGE chipload forced to 0.01: ', self.calculation.chiploadForCalc)
            self.calculation.chiploadForCalc = 0.01

        self.form.FPT_SB.setValue(self.calculation.chiploadForCalc)   # TODO hopefully just need cl value
        #self.calculation.chiploadForCalc(cl)
        self.calculateUpdateGuiAndCentralVars()


    def load_tools(self):                       # Add *list* of ALL TC/Tool names/labels to gui combo box as a list
        if app_mode_FCaddon:
            for idx, tc in enumerate(self.toolControllers):
                self.form.toolController_CB.addItem(tc.Label)
        else:
            # Load standalone tools
            for rowDict in self.toolControllers:
                self.form.toolController_CB.addItem(rowDict["Label"])


    def load_SELECTED_tool_properties(self):    # Get, display(gui) & set(non-gui) TC/Tool props
        tc = self.get_SELECTED_tool_controller()     # find TC/Tool matching combobox SELECTION, return ALL params
        if tc:
            if app_mode_FCaddon:
                self.calculation.tool.Label = tc.Tool.Label
                self.calculation.tool.Diameter = FreeCAD.Units.Quantity(tc.Tool.Diameter).Value
                self.calculation.tool.Flutes = FreeCAD.Units.Quantity(tc.Tool.Flutes).Value
                self.calculation.tool.Material = tc.Tool.Material
                self.calculation.tool.Chipload = FreeCAD.Units.Quantity(tc.Tool.Chipload).Value
                self.calculation.tool.Wear = None
                # FIXME try & extract tool type from name????
                self.calculation.tool.tType = tc.Tool.Label
            else:
                self.calculation.tool = tc
            
            # Change of tool, also triggers updates to:
            # Gui tool values as well as central values for tool &
            # new WOC/DOC & new lookup/calc of SS, CL
            self.set_tool_properties()
        else:
            print('FAILED to load_SELECTED_tool_properties', tc, tc.tool)


    def get_SELECTED_tool_controller(self):
        ''' find TC/Tool matching combobox SELECTION, return ALL params'''
        tcStr = self.form.toolController_CB.currentText()
        if app_mode_FCaddon:
            jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
            for job in jobs:
                for tc in job.Tools.Group:
                    if tc.Label == tcStr:
                        return tc
        else:
            tools_sa = PathFeedsAndSpeeds.load_tools_standalone_only()
            for rowDict in tools_sa:
                tool_sa = PathFeedsAndSpeeds.Tool()
                tool_sa.Label = rowDict["Label"]
                if tool_sa.Label == tcStr:
                    #print('matched tool names', tool_sa.Label, '\t', tcStr)
                    tool_sa.Diameter = rowDict["Diameter"]
                    tool_sa.Flutes = rowDict["Flutes"]
                    tool_sa.Material = rowDict["Material"]
                    tool_sa.tType = rowDict["tType"]
                    return tool_sa

        return None


    def set_tool_properties(self):
        self.form.toolDia_LE.setText(str(self.calculation.tool.Diameter))
        self.form.flutes_SB.setValue(self.calculation.tool.Flutes)
        if self.calculation.tool.Material == "HSS":
            self.form.hss_RB.setChecked(True)
        elif self.calculation.tool.Material == "Carbide":
            self.form.cbd_RB.setChecked(True)
        else:
            print("Unknown Tool material: ", self.calculation.tool.Material)
            
        try:
            self.form.toolType_LE.setText(self.calculation.tool.tType)
        except:
            print("not in detailed gui - OR toolType_LE NOT YET IN Guided gui's")

        # Changed tool, so update WOC/DOC, SS, CL & CT, then re-calc outputs

        #fixme SHOULD implement/use Engagment_typ/Operation Type
        #       2, really should use self.calculation.WOC / DOC
        # change so *CHANGED tool SELECTION* updates self.WOC / DOC
        self.calculation.WOC = round(self.calculation.tool.Diameter / 5, 3)
        self.calculation.DOC = self.calculation.tool.Diameter
        self.form.WOC_SP.setText(str(self.calculation.WOC))
        self.form.DOC_SP.setText(str(self.calculation.DOC))

        self.calculation.updateSurfaceSpeed()
        self.form.ss_LE.setText(str(self.calculation.surfaceSpeed))
        
        self.calculation.updateChipload()
        self.form.FPT_SB.setValue(self.calculation.chiploadForCalc)
        
        self.calculateUpdateGuiAndCentralVars()


    def update_tool_controller_FC_ONLY(self):
        if app_mode_FCaddon:
            tc = self.get_SELECTED_tool_controller()

            if tc:
                # TODO: Add a confirmation dialog
                # FIXME TEST/check values back in FC - saw ~60x!!!!
                tc.HorizFeed = self.calculation.hFeed
                tc.VertFeed = self.calculation.vFeed
                tc.SpindleSpeed = self.calculation.rpm
        # else:
        #   No Tool (controller) update as FreeCAD not running in standalone mode


    # FIXME - just temp name change until get my brain back on track/awake...
    def calculateUpdateGuiAndCentralVars(self):
        if self.calculation.set_stockMaterial is None:
            return
        if not self.calculation.chiploadForCalc:
            return

        self.calculation.rpmOverideValue = self.form.rpm_LE.text()
        
        if not self.form.rpm_LE.text() == "":
            self.form.rpm_result.setEnabled(False)
        else:
            self.form.rpm_result.setEnabled(True)

        self.calculation.calculate()
        
        self.form.rpm_result.setText(str(self.calculation.rpm))
        self.form.hfeed_result.setText(str(self.calculation.hFeed) + " mm/min")
        self.form.vfeed_result.setText(str(self.calculation.vFeed) + " mm/min")
        self.form.hp_result.setText(str(round(self.calculation.millingPower / 746, 2)) + " hp / " + str(round(self.calculation.millingPower, 2)) + " watts")


    def show(self):
        if app_mode_FCaddon:
            self.form.exec_()
        else:
            self.form.show()

    def reject(self):
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
        # print (panel)
        # print (panel.form)
        panel.form.exec_()
        # panel.show()
    except Exception as err:
        print(" 'My function' Failed. " "{err}\n".format(err=str(err)))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


# standalone mode only
if __name__ == "__main__":
    # run standalone without FreeCAD
    #   FeedsAndSpeedsConfig.app_mode_FCaddon = False
    #   if FeedsAndSpeedsConfig.app_mode_FCaddon == False:
    # If no command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # ATM only show FeedsAndSpeeds as form, not main window
    #    .... keeps standalone vs FreeCAD code differences simpler
    # window = QWidget()
    # window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Show()
    panel = FeedSpeedPanel()
    panel.show()

    # Start the event loop.
    # app.exec()
    sys.exit(app.exec_())
