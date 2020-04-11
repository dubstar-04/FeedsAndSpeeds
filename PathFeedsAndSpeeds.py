# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import FreeCAD,FreeCADGui
import math 
from bisect import bisect_right
from PySide import QtGui, QtCore
from PySide.QtGui import QApplication, QDialog, QMainWindow

import PathScripts.PathGui as PathGui

## Interpolate Example from: https://stackoverflow.com/questions/7343697/how-to-implement-linear-interpolation
class Interpolate:
    def __init__(self, x_list, y_list):
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x_list must be in strictly ascending order!")
        self.x_list = x_list
        self.y_list = y_list
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]

    def __call__(self, x):
        if not (self.x_list[0] <= x <= self.x_list[-1]):
            raise ValueError("x out of bounds!")
        if x == self.x_list[-1]:
            return self.y_list[-1]
        i = bisect_right(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])


class FeedSpeedPanel:
    def __init__(self):

        #Build GUI
        ui = FreeCADGui.UiLoader()
        self.dialog = QtGui.QDialog()
        self.dialog.resize(300,100)
        self.dialog.setWindowTitle("Feeds and Speeds") 

        mainLayout = QtGui.QFormLayout(self.dialog)
        self.tabWidget = QtGui.QTabWidget() 

        self.material_CB = QtGui.QComboBox()
        mainLayout.addRow("Material:", self.material_CB)

        toolMatLayout = QtGui.QHBoxLayout()
        self.hss_RB = QtGui.QRadioButton("HSS")
        self.cbd_RB = QtGui.QRadioButton("Carbide")

        toolMatLayout.addWidget(self.hss_RB)
        toolMatLayout.addWidget(self.cbd_RB)

        mainLayout.addRow("Tool:", toolMatLayout)


        #####################################
        ##           Milling Page          ##
        #####################################

        tabPageMilling = QtGui.QWidget()
        millingLayout = QtGui.QFormLayout(tabPageMilling)
        
        self.toolDia_LE = ui.createWidget("Gui::InputField")
        millingLayout.addRow("Tool Diameter:", self.toolDia_LE)

        self.flutes_SB = QtGui.QSpinBox()
        millingLayout.addRow("No. Flutes:", self.flutes_SB)

        self.FPT_LE = ui.createWidget("Gui::InputField")
        millingLayout.addRow("FPT:", self.FPT_LE)

        self.WOC_SP = ui.createWidget("Gui::InputField")
        millingLayout.addRow("WOC:", self.WOC_SP)

        self.DOC_SP = ui.createWidget("Gui::InputField")
        millingLayout.addRow("DOC:", self.DOC_SP)

        #####################################
        ##           Drilling Page         ##
        #####################################

        tabPageDrilling = QtGui.QWidget()
        drillingLayout = QtGui.QFormLayout(tabPageDrilling)

        self.drillDia_LE = ui.createWidget("Gui::InputField")
        drillingLayout.addRow("Drill Diameter:", self.drillDia_LE)

        self.drillFPT_LE = ui.createWidget("Gui::InputField")
        drillingLayout.addRow("FPT:", self.drillFPT_LE)

        depthNote = QtGui.QLabel("\nNote: Peck drilling should be used when hole depth > 4 x tool diameter")
        drillingLayout.addRow(depthNote)

        #####################################
        ##             Results             ##
        #####################################

        resultFrame = QtGui.QFrame()
        frameLayout = QtGui.QFormLayout()
        rpmLayout = QtGui.QHBoxLayout()
        
        self.rpm_result = QtGui.QLabel()
        rpmLayout.addWidget(self.rpm_result)
        self.rpm_LE = QtGui.QLineEdit()
        
        rpmLayout.addWidget(self.rpm_LE)
        rpmLayout.insertStretch(1)
        frameLayout.addRow("RPM:", rpmLayout)

        self.feed_result= QtGui.QLabel()
        frameLayout.addRow("Feed:", self.feed_result)

        self.hp_result = QtGui.QLabel()
        frameLayout.addRow("Power:", self.hp_result)
    
        resultFrame.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        resultFrame.setLayout(frameLayout)

        ### Asssemble UI
        mainLayout.addRow(self.tabWidget)
        mainLayout.addRow(resultFrame)
        self.tabWidget.addTab(tabPageMilling, "Milling")
        self.tabWidget.addTab(tabPageDrilling, "Drilling")

        ### Set Defaults
        self.toolDia = 6

        ### Init 
        self.load_materials()
        self.setup_ui()
        self.calculate()
        self.reset()

        ### connect
        self.tabWidget.currentChanged.connect(self.calculate)
        self.material_CB.currentIndexChanged.connect(self.calculate)
        self.hss_RB.toggled.connect(self.calculate)
        self.cbd_RB.toggled.connect(self.calculate)
        self.toolDia_LE.textChanged.connect(self.calculate)
        self.flutes_SB.valueChanged.connect(self.calculate)
        self.FPT_LE.textChanged.connect(self.calculate)
        self.WOC_SP.valueChanged.connect(self.calculate)
        self.DOC_SP.valueChanged.connect(self.calculate)
        self.rpm_LE.textChanged.connect(self.calculate)
        self.drillDia_LE.textChanged.connect(self.calculate)
        self.drillFPT_LE.textChanged.connect(self.calculate)

        ### Show the dialog
        self.dialog.show()
        self.dialog.exec_()

    def load_materials(self):
        ## Data from Machineries Handbook 28. 
        ## Kp: Tables 1a, 1b 
        ## Brinell Hardness: http://www.matweb.com

        ## ss_hss = surface speed (m/min) for milling with high speed steel tools (hss)
        ## ss_cbd = surface speed (m/min) for milling with carbide tools
        ## ss_drill_hss = surface speed (m/min) for drilling with high speed steel tools (hss)
        ## ss_drill_cbd = surface speed (m/min) for drilling with carbide tools
        ## ref: 1 ft/min = 0.3048 m/min

        self.materials = [
         { "material": "Softwood",                 "ss_hss": 225,  "ss_cbd": 255,   "ss_drill_hss": 185,   "ss_drill_cbd": 205,    "kp": 0.5,      "brinell": 0 },
         { "material": "Hardwood",                 "ss_hss": 145,  "ss_cbd": 275,   "ss_drill_hss": 115,   "ss_drill_cbd": 400,    "kp": 0.75,     "brinell": 0 },
         { "material": "Soft Plastics",            "ss_hss": 225,  "ss_cbd": 255,   "ss_drill_hss": 185,   "ss_drill_cbd": 205,    "kp": 0.5,      "brinell": 0 },
         { "material": "Hard Plastics",            "ss_hss": 225,  "ss_cbd": 275,   "ss_drill_hss": 115,   "ss_drill_cbd": 400,    "kp": 0.75,     "brinell": 0 },
         { "material": "Aluminium (6061)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 135,   "ss_drill_cbd": 310,    "kp": 0.90,     "brinell": 95  },
         { "material": "Aluminium (7075)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 125,   "ss_drill_cbd": 310,    "kp": 0.90,     "brinell": 150 },
         { "material": "Aluminium (Cast)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 135,   "ss_drill_cbd": 310,    "kp": 0.68,     "brinell": 150 },
         { "material": "Brass (Hard)",             "ss_hss": 200,  "ss_cbd": 395,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 2.27,     "brinell": 120 },
         { "material": "Brass (Medium)",           "ss_hss": 175,  "ss_cbd": 350,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 1.36,     "brinell": 120 },
         { "material": "Brass (Soft)",             "ss_hss": 125,  "ss_cbd": 300,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 0.68,     "brinell": 120 },
         { "material": "Carbon Steel",             "ss_hss": 35,   "ss_cbd": 120,   "ss_drill_hss": 25,    "ss_drill_cbd": 90,     "kp": 1.88,     "brinell": 130 },
         { "material": "Tool Steel",               "ss_hss": 12,   "ss_cbd": 45,    "ss_drill_hss": 10,    "ss_drill_cbd": 30,     "kp": 1.88,     "brinell": 400 },
         { "material": "Stainless (303)",          "ss_hss": 25,   "ss_cbd": 85,    "ss_drill_hss": 20,    "ss_drill_cbd": 65,     "kp": 2.07,     "brinell": 200 },
         { "material": "Stainless (304)",          "ss_hss": 10,   "ss_cbd": 37.5,  "ss_drill_hss": 10,    "ss_drill_cbd": 30,     "kp": 2.07,     "brinell": 125 },
         { "material": "Stainless (316)",          "ss_hss": 7.5,  "ss_cbd": 25,    "ss_drill_hss": 5,     "ss_drill_cbd": 20,     "kp": 2.07,     "brinell": 80 },
        ]


        self.powerConstant = {
            ## Constant Power
            ## Data from Machineries Handbook 28. 
            ## Table 2
            ## mm/tooth : C
             0.02: 1.70,
             0.05: 1.40,
             0.07: 1.30,
             0.10: 1.25,
             0.12: 1.20,
             0.15: 1.15,
             0.18: 1.11,
             0.20: 1.08,
             0.22: 1.06,
             0.25: 1.04,
             0.28: 1.01,
             0.30: 1.00,
             0.33: 0.98,
             0.35: 0.97,
             0.38: 0.95,
             0.40: 0.94,
             0.45: 0.92,
             0.50: 0.90,
             0.55: 0.88,
             0.60: 0.87,
             0.70: 0.84,
             0.75: 0.83,
             0.80: 0.82,
             0.90: 0.80,
             1.00: 0.78,
             1.50: 0.72
           }

    def setup_ui(self):    
    
        ### load materials
        for material in (d['material'] for d in self.materials):
            self.material_CB.addItem(material)

        ### set tool material
        self.hss_RB.setChecked(True)    

        ### load widget data
        self.toolDia_LE.setText(FreeCAD.Units.Quantity(float(self.toolDia),FreeCAD.Units.Length).getUserPreferred()[0])
        self.flutes_SB.setValue(2)
        self.FPT_LE.setText(FreeCAD.Units.Quantity(float(self.toolDia * 0.01),FreeCAD.Units.Length).getUserPreferred()[0])   
        self.WOC_SP.setText(FreeCAD.Units.Quantity(float(self.toolDia * 0.2 ),FreeCAD.Units.Length).getUserPreferred()[0])
        self.DOC_SP.setText(FreeCAD.Units.Quantity(float(self.toolDia ),FreeCAD.Units.Length).getUserPreferred()[0])
        self.drillDia_LE.setText(FreeCAD.Units.Quantity(float(self.toolDia),FreeCAD.Units.Length).getUserPreferred()[0])
        self.drillFPT_LE.setText(FreeCAD.Units.Quantity(float(self.toolDia * 0.01),FreeCAD.Units.Length).getUserPreferred()[0]) 
        self.rpm_LE.setPlaceholderText("RPM Overide")

    def calculate(self):

        material = self.material_CB.currentText()
        rpm_overide = self.rpm_LE.text()

        if self.tabWidget.currentIndex() == 0:
            # calculate for milling
            toolDia = FreeCAD.Units.Quantity(self.toolDia_LE.text()).Value
            flutes = self.flutes_SB.value()
            feedPerTooth = FreeCAD.Units.Quantity(self.FPT_LE.text()).Value
            WOC = FreeCAD.Units.Quantity(self.WOC_SP.text())
            DOC = FreeCAD.Units.Quantity(self.DOC_SP.text())         
            W = 1.1 ## Tool Wear pg: 1048
            ss_by_material = "ss_hss" if self.hss_RB.isChecked() else "ss_cbd"
        else:
            # calculate for drilling
            toolDia = FreeCAD.Units.Quantity(self.drillDia_LE.text()).Value
            feedPerTooth = FreeCAD.Units.Quantity(self.drillFPT_LE.text()).Value
            W = 1.3 ## Tool Wear pg: 1048
            ss_by_material = "ss_drill_hss" if self.hss_RB.isChecked() else "ss_drill_cbd"

        if not feedPerTooth:
            return

        surfaceSpeed = next(item for item in self.materials if item["material"] == material).get(ss_by_material)
        Kp = next(item for item in self.materials if item["material"] == material).get("kp")
        ## C = Power Constant
        fptValues = list(self.powerConstant.keys())
        cValues = list(self.powerConstant.values())
        interp = Interpolate(fptValues, cValues)
        try:
            C = interp(feedPerTooth)
        except:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Feed per tooth has exceeded the recommended range. 0.02 - 1.5")
            msgBox.exec_()
            return

        rpm = int((1000 * surfaceSpeed) / (math.pi * toolDia))
        calc_rpm = rpm
        
        if not rpm_overide == "":
            calc_rpm = float(rpm_overide)
            self.rpm_result.setEnabled(False)
        else:
            self.rpm_result.setEnabled(True)

        
        feed = int(calc_rpm * feedPerTooth * flutes) if self.tabWidget.currentIndex() == 0 else int(feedPerTooth * calc_rpm)

        ##### Machining Power #####
        ## Calculation to Machineries Handbook: Pg 1058

        print("WOC", WOC, " DOC", DOC, " Feed", feed)

        ## Material Removal Rate: Pg 1049
        Q = float((WOC * DOC * feed) / 60000) ##cm^3/s
        
        ## Machine Efficiency: Pg 1049
        E = 0.80 

        print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", W, " E", E)

        ## Power Required at the cutter: Pg 1048
        Pc = Kp * C * Q * W

        ## Power Required at the motor
        Pm = Pc / E

        # Convert to Hp
        Hp = Pm * 1.341

        print("power", Pc, Pm, Hp)

        self.rpm_result.setText(str(rpm))
        self.feed_result.setText(str(feed) + " mm/min")
        self.hp_result.setText(str(round(Hp, 2)) + " hp")

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






