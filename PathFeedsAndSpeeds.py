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

def load_materials():
    ## Data from Machineries Handbook 28. 
    ## Kp: Tables 1a, 1b 
    ## Brinell Hardness: http://www.matweb.com

    ## ss_hss = surface speed (m/min) for milling with high speed steel tools (hss)
    ## ss_cbd = surface speed (m/min) for milling with carbide tools
    ## ss_drill_hss = surface speed (m/min) for drilling with high speed steel tools (hss)
    ## ss_drill_cbd = surface speed (m/min) for drilling with carbide tools
    ## ref: 1 ft/min = 0.3048 m/min

    materials = [
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

    return materials


def load_powerConstant():
    powerConstant = {
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
        
    return powerConstant

class Tool:
    def __init__(self, toolDia=6, flutes=3):

        self.toolDia = toolDia
        self.flutes = flutes

class FSCalculation:
    def __init__(self):

        self.opType = 'Milling'
        self.material = None
        self.rpm_overide = None
        self.ss_by_material = None
        self.toolWear = None
        self.feedPerTooth = None
        self.WOC = None
        self.DOC = None
    

    def calculate(self, tool):

        print('calculate for opType: ', self.opType)
        materials = load_materials()
        powerConstant = load_powerConstant()
        surfaceSpeed = next(item for item in materials if item["material"] == self.material).get(self.ss_by_material)
        Kp = next(item for item in materials if item["material"] == self.material).get("kp")
        ## C = Power Constant
        fptValues = list(powerConstant.keys())
        cValues = list(powerConstant.values())
        interp = Interpolate(fptValues, cValues)

        try:
            C = interp(self.feedPerTooth)
        except:
            print("Feed per tooth has exceeded the recommended range. 0.02 - 1.5")
            return

        rpm = int((1000 * surfaceSpeed) / (math.pi * tool.toolDia))
        calc_rpm = rpm
        
        if self.rpm_overide:
            calc_rpm = float(self.rpm_overide)
        
        feed = int(calc_rpm * self.feedPerTooth * tool.flutes) if self.opType == 'Milling' else int(self.feedPerTooth * calc_rpm)

        ##### Machining Power #####
        ## Calculation to Machineries Handbook: Pg 1058

        print("WOC", self.WOC, " DOC", self.DOC, " Feed", feed)

        ## Material Removal Rate: Pg 1049
        Q = float((self.WOC * self.DOC * feed) / 60000) ##cm^3/s
        
        ## Machine Efficiency: Pg 1049
        E = 0.80 

        print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", self.toolWear, " E", E)

        ## Power Required at the cutter: Pg 1048
        Pc = Kp * C * Q * self.toolWear

        ## Power Required at the motor
        Pm = Pc / E

        # Convert to Hp
        Hp = Pm * 1.341

        print("power", Pc, Pm, Hp)

        return rpm, feed, Hp







