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

def getInterpolatedValue(inputDict, value):
    keys = list(inputDict.keys())
    values = list(inputDict.values())
    interpolation = Interpolate(keys, values)
    try:
        return interpolation(value)
    except:
        print("Interpolated value outside the expected range")
        return None

def load_materials():
    ## Data from Machineries Handbook 28. 
    ## Kp: Tables 1a, 1b 
    ## Brinell Hardness: http://www.matweb.com

    ## ss_hss = surface speed (m/min) for milling with high speed steel tools (hss)
    ## ss_cbd = surface speed (m/min) for milling with carbide tools
    ## ss_drill_hss = surface speed (m/min) for drilling with high speed steel tools (hss)
    ## ss_drill_cbd = surface speed (m/min) for drilling with carbide tools
    ## Kd = workMaterialFactor from Table 31
    ## ref: 1 ft/min = 0.3048 m/min

    materials = [
        { "material": "Softwood",                 "ss_hss": 225,  "ss_cbd": 255,   "ss_drill_hss": 185,   "ss_drill_cbd": 205,    "kp": 0.5,      "brinell": 0,     "Kd": 3000 },
        { "material": "Hardwood",                 "ss_hss": 145,  "ss_cbd": 275,   "ss_drill_hss": 115,   "ss_drill_cbd": 400,    "kp": 0.75,     "brinell": 0,     "Kd": 4000 },
        { "material": "Soft Plastics",            "ss_hss": 225,  "ss_cbd": 255,   "ss_drill_hss": 185,   "ss_drill_cbd": 205,    "kp": 0.5,      "brinell": 0,     "Kd": 2000 },
        { "material": "Hard Plastics",            "ss_hss": 225,  "ss_cbd": 275,   "ss_drill_hss": 115,   "ss_drill_cbd": 400,    "kp": 0.75,     "brinell": 0,     "Kd": 2000 },
        { "material": "Aluminium (6061)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 135,   "ss_drill_cbd": 310,    "kp": 0.90,     "brinell": 95,    "Kd": 7000  },
        { "material": "Aluminium (7075)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 125,   "ss_drill_cbd": 310,    "kp": 0.90,     "brinell": 150,   "Kd": 7000 },
        { "material": "Aluminium (Cast)",         "ss_hss": 175,  "ss_cbd": 395,   "ss_drill_hss": 135,   "ss_drill_cbd": 310,    "kp": 0.68,     "brinell": 150,   "Kd": 7000 },
        { "material": "Brass (Hard)",             "ss_hss": 200,  "ss_cbd": 395,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 2.27,     "brinell": 120,   "Kd": 14000 },
        { "material": "Brass (Medium)",           "ss_hss": 175,  "ss_cbd": 350,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 1.36,     "brinell": 120,   "Kd": 14000 },
        { "material": "Brass (Soft)",             "ss_hss": 125,  "ss_cbd": 300,   "ss_drill_hss": 115,   "ss_drill_cbd": 350,    "kp": 0.68,     "brinell": 120,   "Kd": 7000 },
        { "material": "Carbon Steel",             "ss_hss": 35,   "ss_cbd": 120,   "ss_drill_hss": 25,    "ss_drill_cbd": 90,     "kp": 1.88,     "brinell": 130,   "Kd": 24000},
        { "material": "Tool Steel",               "ss_hss": 12,   "ss_cbd": 45,    "ss_drill_hss": 10,    "ss_drill_cbd": 30,     "kp": 1.88,     "brinell": 400,   "Kd": 340000 },
        { "material": "Stainless (303)",          "ss_hss": 25,   "ss_cbd": 85,    "ss_drill_hss": 20,    "ss_drill_cbd": 65,     "kp": 2.07,     "brinell": 200,   "Kd": 200000 },
        { "material": "Stainless (304)",          "ss_hss": 10,   "ss_cbd": 37.5,  "ss_drill_hss": 10,    "ss_drill_cbd": 30,     "kp": 2.07,     "brinell": 125,   "Kd": 22000 },
        { "material": "Stainless (316)",          "ss_hss": 7.5,  "ss_cbd": 25,    "ss_drill_hss": 5,     "ss_drill_cbd": 20,     "kp": 2.07,     "brinell": 80,    "Kd": 24000 },
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

def load_feedFactor():
    feedFactor = {
        ## Feed Factor
        ## Data from Machineries Handbook 28. 
        ## Table 33
        ## mm/rev : Ff
            0.01: 0.025,
            0.03: 0.060,
            0.05: 0.091,
            0.07: 0.133,
            0.10: 0.158,
            0.12: 0.183,
            0.15: 0.219,
            0.18: 0.254,
            0.20: 0.276,
            0.22: 0.298,
            0.25: 0.330,
            0.30: 0.382,
            0.35: 0.432,
            0.40: 0.480,
            0.45: 0.528,
            0.50: 0.574,
            0.55: 0.620,
            0.65: 0.780,
            0.75: 0.794,
            0.90: 0.919,
            1.00: 0.100,
            1.25: 1.195
        }
        
    return feedFactor

def load_diameterFactors():
        ## Diamater Factors
        ## Data from Machineries Handbook 28. 
        ## Table 34
        ## mm, Fm
    diameterFactors = {
        1.60: 2.33, 
        2.40: 4.84,
        3.20: 8.12,
        4.00: 12.12,
        4.80: 16.84,
        5.60: 22.22, 
        6.40: 28.26, 
        7.20: 34.93, 
        8.00: 42.22, 
        8.80: 50.13, 
        9.50: 57.53, 
        11.00: 74.90, 
        12.50: 94.28, 
        14.50: 123.1, 
        16.00: 147.0,
        17.50: 172.8,
        19.00: 200.3, 
        20.00: 219.7, 
        22.00: 260.8,
        24.00: 305.1,
        25.50: 340.2,
        27.00: 377.1,
        28.50: 415.6,
        32.00: 512.0,
        35.00: 601.6,
        38.00: 697.6,
        42.00: 835.3,
        45.00: 945.8,
        48.00: 1062,
        50.00: 1143,
        58.00: 1493,
        64.00: 1783,
        70.00: 2095,
        76.00: 2429,
        90.00: 3293,
        100.00: 3981
    }
    return diameterFactors

class Tool:
    def __init__(self, toolDia=6, flutes=3):

        self.toolDia = toolDia
        self.flutes = flutes

class Cnc_limits:
    """ Define limits of your machines feed rate, rp, and power 
    
        Defaults are low to help test over rides & also are for my low end home made CNC"""
    
    def __init__(self, feedMax=1000, rpmMin = 1000, rpmMax=12000, power=500):
    
        self.cncFeedMax = feedMax   # mm/min
        self.cncRpmMin = rpmMin
        self.cncRpmMax = rpmMax
        self.cncPower = power       # in watts

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
        self.limits = None
 
    def calculate(self, tool):

        print('calculate for opType: ', self.opType)
        materials = load_materials()
        surfaceSpeed = next(item for item in materials if item["material"] == self.material).get(self.ss_by_material)
        Kp = next(item for item in materials if item["material"] == self.material).get("kp")
        ## C = Power Constant
        C = getInterpolatedValue(load_powerConstant(), self.feedPerTooth) 
        rpm = int((1000 * surfaceSpeed) / (math.pi * tool.toolDia))
        calc_rpm = rpm
        
        if self.rpm_overide:
            calc_rpm = float(self.rpm_overide)

        ## Machine Efficiency: Pg 1049
        E = 0.80 
        
        ##### Machining Power #####
        if self.opType == 'Milling':
            feed = int(calc_rpm * self.feedPerTooth * tool.flutes)
            ## Calculation to Machineries Handbook: Pg 1058
            #print("WOC", self.WOC, " DOC", self.DOC, " Feed", feed)
            ## Material Removal Rate: Pg 1049
            Q = float((self.WOC * self.DOC * feed) / 60000) ##cm^3/s
            #print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", self.toolWear, " E", E)
            ## Power Required at the cutter: Pg 1048
            Pc = Kp * C * Q * self.toolWear

        if self.opType == 'Drilling':
            feed = int(self.feedPerTooth * calc_rpm)
            # Kd = Work material factor (Table 31)
            # Ff = Feed factor (Table 33)
            # FM = Torque factor for drill diameter (Table 34)
            # A = Chisel edge factor for torque (Table 32)
            # w = Web thickness at drill point (See Table 32)

            Kd = next(item for item in materials if item["material"] == self.material).get("Kd")
            Ff = getInterpolatedValue(load_feedFactor(), self.feedPerTooth) 
            Fm = getInterpolatedValue(load_diameterFactors(), tool.toolDia)
            A = 1.085 #fixed value based on standard 118 deg drill. Table 32
            W = 0.18 * tool.toolDia #fixed value based on standard 118 deg drill. Table 32

            M = Kd * Ff * Fm * A * W / 40000    #pg 1054
            Pc = M * calc_rpm / 9550            #pg 1054
        

        ## Power Required at the motor
        Pm = Pc / E
        # Convert to Hp
        Hp = Pm * 1.341
        #print("power", Pc, Pm, Hp)
        return calc_rpm, feed, Hp


# TODO change tool & limits to be part of FSCalculation & no need pass around??
    def printInputs(self, tool, limits):
        print("\n\t\t -- Display Inputs to the 'Feed and Speed Calculator'")
        print("\tCNC limits:- FeedMax: %d, RpmMin: %d, RpmMax: %d, PowerMax:  %d" % (limits.cncFeedMax, limits.cncRpmMin, limits.cncRpmMax, limits.cncPower))
        print("\ttool:- Dia: %.2f, flutes: %d, material: %s" % (tool.toolDia, tool.flutes, self.ss_by_material))
        print("\tmaterial: %s" % self.material)
        print("\topType: %s, toolWear: %.2f" % (self.opType, self.toolWear))
        print("\tfeedPerTooth: %.3f, WOC: %.2f, DOC: %.2f" % (self.feedPerTooth, self.WOC, self.DOC))
        if self.opType == False :
            print('\tNote: Use Peck drilling if hole depth >4x tool dia, ie ' + str(tool.toolDia * 4))
        print(" --- Display Inputs end\n")

    def initDefaults(self):

        # Set the limits of your CNC Mill. You can pass in your own values to over ride the defaults.
        limits = Cnc_limits()   #Defaults: feedMax=1000, rpmMin = 1000, rpmMax=12000, power=500
        # fs = PathFeedsAndSpeeds.FSCalculation()

        # Set params of the tool. Note, tool material is set below for either Milling or Drilling.
        tool = Tool()
        tool.toolDia = float(6.0)
        tool.flutes = 2

        self.opType = 'Milling'   # operation is Milling or Drilling
        # Material to be cut. Find exact name from above # REFERENCE: Materials list.
        self.material = "Hard Plastics"  #"Hardwood"   # "Aluminium (6061)"

        # Milling or Drilling specific params.
        # Note you can for set parameters to be dependant upon others, 
        #   for eg: DOC to be a fraction of your Tool dia, eg: self.DOC = tool.toolDia/2
        if self.opType == 'Milling' :
            self.feedPerTooth = float(0.060)
            self.WOC = 1.2
            self.DOC = 6
            self.toolWear = 1.1                      ## Tool Wear pg: 1048
            self.ss_by_material = "ss_cbd"           # "ss_hss" "ss_cbd"
        else:
            self.feedPerTooth = float(0.060)
            self.toolWear = 1.3                      ## Tool Wear pg: 1048
            self.ss_by_material = "ss_drill_hss"     # "ss_drill_hss' "ss_drill_cbd"
            if tool.toolDia:
                print('Note: Use Peck drilling if hole depth >4x tool dia, ie ' + str(tool.toolDia * 4))
        return tool, limits
     
    def calcWithAutoOverrides(self, tool, limits):

        rpm, feed, Hp = self.calculate(tool) 
        print("\trpm %d, feed %d, Hp %.2f & Watts %d" % (rpm, feed, Hp, (Hp*745.6999)))
        if rpm > limits.cncRpmMax:
            self.rpm_overide = limits.cncRpmMax
            rpm, feed, Hp = self.calculate(tool) 
            print("\t >>>OVERRIDING RPM to cnc max rpm")
            print("\t rpm %d, feed %d, Hp  %.2f & Watts  %d" % (rpm, feed, Hp, Hp*745.6999))

        if rpm < limits.cncRpmMin:
            self.rpm_overide = limits.cncRpmMin
            rpm, feed, Hp = self.calculate(tool) 
            print("\t >>>OVERRIDING RPM to cnc *MIN* rpm")
            print("\t rpm %d, feed %d, Hp  %.2f & Watts  %d" % (rpm, feed, Hp, Hp*745.6999))

        if feed > limits.cncFeedMax:
            self.rpm_overide = rpm * limits.cncFeedMax/feed
            rpm, feed, Hp = self.calculate(tool) 
            print("\t >>>OVERRIDING & reducing FEED ")
            print("\t rpm %d, feed %d, Hp  %.2f & Watts  %d" % (rpm, feed, Hp, Hp*745.6999))

        if  Hp*745.6999 > limits.cncPower:
            self.rpm_overide = feed * limits.cncPower/Hp*745.6999
            rpm, feed, Hp = self.calculate(tool) 
            print("\t >>>OVERRIDING Power required & reducing FEED ")
            print("\t rpm %d, feed %d, Hp  %.2f & Watts  %d" % (rpm, feed, Hp, Hp*745.6999))
        return (rpm, feed, Hp)

