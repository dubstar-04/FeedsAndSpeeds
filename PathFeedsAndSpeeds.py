# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import math
from bisect import bisect_right
# import sys
import csv

# TODO remove unused vars eg ?rpmBeforeLimit? & ohters??
# TODO consistent approach for override & limit intermediate vars!!!


# FIXME: Plenty of hardcoded values like HSS, carbide, drill and some # constants move to user prefs!!
# ...or at least all together at top of this file as vars/constants


# FIXME: interpolation errors when lookups out of range - eg small dia tools and/or very soft/hard materials
#        could look to extending data (eg plot trend line, then add raw data, or convert to equation as did with ChipLoad
#   MAYBE add msg to user when extrapolating outside "core data"...even though data already still quite suspect!!!

# FIXME: ENFORCE or give msg if WOC <> tool.dia!!!!
# FIXME: & ditto if DOC > tool.length/height/whatever called, BUT ONLY if prop existis or > 0!!!!

# TODO Cutting strategies operation-engagement, conventional/climb, HSM, REST...
# TODO Add ToolLife/ajusment see MC HB table 15e p1101
# TODO cutting fluids


# Interpolate Example from: https://stackoverflow.com/questions/7343697/how-to-implement-linear-interpolation
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


def getInterpolatedValue(inputDict, value, callerMsg):
    keys = list(inputDict.keys())
    values = list(inputDict.values())
    interpolation = Interpolate(keys, values)
    try:
        return interpolation(value)
    except ValueError:
        # TODO should pass in & print here WHICH var was looking up!!!!
        print("Interpolated value outside the expected range for: ", callerMsg, value)
        return None


def load_powerConstant():
    powerConstant = {
        # Constant Power
        # Data from Machineries Handbook 28.
        # Table 2
        # mm/tooth : C
        # Extrapolated 2 values at start & 6 at bottom
        # to cater for smaller & larger chiploads
        # C = 0.785501584309353 * Chipload^-0.197425892437151
            0.01: 1.95,  # noqa: E131
            0.015: 1.80, # noqa: E131
            0.02: 1.70,  # noqa: E131
            0.05: 1.40,  # noqa: E131
            0.07: 1.30,  # noqa: E131
            0.10: 1.25,  # noqa: E131
            0.12: 1.20,  # noqa: E131
            0.15: 1.15,  # noqa: E131
            0.18: 1.11,  # noqa: E131
            0.20: 1.08,  # noqa: E131
            0.22: 1.06,  # noqa: E131
            0.25: 1.04,  # noqa: E131
            0.28: 1.01,  # noqa: E131
            0.30: 1.00,  # noqa: E131
            0.33: 0.98,  # noqa: E131
            0.35: 0.97,  # noqa: E131
            0.38: 0.95,  # noqa: E131
            0.40: 0.94,  # noqa: E131
            0.45: 0.92,  # noqa: E131
            0.50: 0.90,  # noqa: E131
            0.55: 0.88,  # noqa: E131
            0.60: 0.87,  # noqa: E131
            0.70: 0.84,  # noqa: E131
            0.75: 0.83,  # noqa: E131
            0.80: 0.82,  # noqa: E131
            0.90: 0.80,  # noqa: E131
            1.00: 0.78,  # noqa: E131
            1.50: 0.72,  # noqa: E131
            1.75: 0.70,   # noqa: E131
            2.0: 0.685,   # noqa: E131
            2.5: 0.65,   # noqa: E131
            3.0: 0.63,   # noqa: E131
            4.0: 0.60,   # noqa: E131
            5.0: 0.57,   # noqa: E131
        }  # noqa: E123

    return powerConstant


def load_feedFactor():
    feedFactor = {
        # Feed Factor
        # Data from Machineries Handbook 28.
        # Table 33
        # mm/rev : Ff
            0.01: 0.025,  # noqa: E131
            0.03: 0.060,  # noqa: E131
            0.05: 0.091,  # noqa: E131
            0.07: 0.133,  # noqa: E131
            0.10: 0.158,  # noqa: E131
            0.12: 0.183,  # noqa: E131
            0.15: 0.219,  # noqa: E131
            0.18: 0.254,  # noqa: E131
            0.20: 0.276,  # noqa: E131
            0.22: 0.298,  # noqa: E131
            0.25: 0.330,  # noqa: E131
            0.30: 0.382,  # noqa: E131
            0.35: 0.432,  # noqa: E131
            0.40: 0.480,  # noqa: E131
            0.45: 0.528,  # noqa: E131
            0.50: 0.574,  # noqa: E131
            0.55: 0.620,  # noqa: E131
            0.65: 0.780,  # noqa: E131
            0.75: 0.794,  # noqa: E131
            0.90: 0.919,  # noqa: E131
            1.00: 0.100,  # noqa: E131
            1.25: 1.195  # noqa: E131
    }

    return feedFactor


def load_diameterFactors():
    # Diamater Factors
    # Data from Machineries Handbook 28.
    # Table 34
    # mm, Fm
    diameterFactors = {
        1.60: 2.33,  # noqa: E131
        2.40: 4.84,  # noqa: E131
        3.20: 8.12,  # noqa: E131
        4.00: 12.12,  # noqa: E131
        4.80: 16.84,  # noqa: E131
        5.60: 22.22,   # noqa: E131
        6.40: 28.26,   # noqa: E131
        7.20: 34.93,   # noqa: E131
        8.00: 42.22,   # noqa: E131
        8.80: 50.13,   # noqa: E131
        9.50: 57.53,   # noqa: E131
        11.00: 74.90,   # noqa: E131
        12.50: 94.28,   # noqa: E131
        14.50: 123.1,   # noqa: E131
        16.00: 147.0,  # noqa: E131
        17.50: 172.8,  # noqa: E131
        19.00: 200.3,   # noqa: E131
        20.00: 219.7,   # noqa: E131
        22.00: 260.8,  # noqa: E131
        24.00: 305.1,  # noqa: E131
        25.50: 340.2,  # noqa: E131
        27.00: 377.1,  # noqa: E131
        28.50: 415.6,  # noqa: E131
        32.00: 512.0,  # noqa: E131
        35.00: 601.6,  # noqa: E131
        38.00: 697.6,  # noqa: E131
        42.00: 835.3,  # noqa: E131
        45.00: 945.8,  # noqa: E131
        48.00: 1062,  # noqa: E131
        50.00: 1143,  # noqa: E131
        58.00: 1493,  # noqa: E131
        64.00: 1783,  # noqa: E131
        70.00: 2095,  # noqa: E131
        76.00: 2429,  # noqa: E131
        90.00: 3293,  # noqa: E131
        100.00: 3981  # noqa: E131
    }
    return diameterFactors


def load_materials():
    # Data from Machineries Handbook 28.
    # Kp: Tables 1a, 1b
    # Brinell Hardness: http://www.matweb.com

    # ss = surface speed (m/min) milling or drilling
    # ss_hss = for milling with high speed steel tools (hss)
    # ss_cbd = for milling with Carbide tools
    # ss_drill_hss = for drilling with high speed steel tools (hss)
    # ss_drill_cbd = for drilling with Carbide tools
    # Kd = Work Material factor (Table 31) or is it  p1060 Table 6?
    # ref: 1 ft/min = 0.3048 m/min

    return load_data('materials_ss_cl.csv')


def load_user_prefs():

    return load_data('prefs.csv')


def load_tools_standalone_only():
    return load_data('tools_standalone_only.csv')

# --- csv -----------------------------
# From user imm https://forum.freecadweb.org/viewtopic.php?f=15&t=59856&start=50
# -- any numeric value that can be converted to float is converted to float.


def fitem(item):
    item.strip()
    try:
        item = float(item)
    except ValueError:
        pass
    return item

# -- takes a header list and row list converts it into a dict.
# Numeric values converted to float in the row list wherever possible.


def rowConvert(h, a):
    b = []
    for x in a:
        b.append(fitem(x))
    k = iter(h)
    it = iter(b)
    res_dct = dict(zip(k, it))
    return res_dct


def load_data(dataFile):
    import os
    p = os.path.dirname(__file__)
    # TODO windows path '\' ???
    filename = p + '/' + dataFile

    dataDict = []
    with open(filename, 'r') as csvin:
        alist = list(csv.reader(csvin))
        firstLine = True
        for a in alist:
            if firstLine:
                if len(a) == 0: continue    # noqa: E701
                if len(a) == 1: continue    # noqa: E701
                else:
                    h = a
                    firstLine = False
            else:
                # print(rowConvert(h,a))
                dataDict.append(rowConvert(h, a))

    return dataDict
# --- end csv -----------------------------

# var names match FreeCAD ToolController.Tool to ease standalone code.


class Tool:
    def __init__(self, Label='Endmill 1', Diameter=6.01, Flutes=3, Material='HSS', Chipload=0.01, Wear = 1.1, tType = 'endmill'):
        self.Label = Label
        self.Diameter = Diameter
        self.Flutes = Flutes
        self.Material = Material
        self.Chipload = Chipload
        self.Wear = Wear
        self.tType = tType			# in FC derive from ShapeFile?? & Standalone derive from ?? ...starting with Typew cole in Tool csv file.
		# Default FC Tool obj.BitPropertyNames: ['Chipload', 'CuttingEdgeHeight', 'Diameter', 'Flutes', 'Length', 'Material', 'ShankDiameter']
		# Attributes are: 'Chipload', 'Flutes', 'Material'...all already in prop list, but classified as attrib in gui
		# Also Name & ShapeFile

        # Poss extend with
        # self.toolCoating = None
        # self.toolStickout = None
        # etc....

    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            print('\t\t---------------------')
            for k, v in items:
                #print(f"attribute tool.{k}    value: {v}")
                print(f"\t\ttool.{k} = {v}")
            print('\t\t---------------------')

        return items


class Cnc_limits:
    """ Define limits of your machines feed rate, rp, and power
        Defaults low for override tests"""

    def __init__(self, feedMax=1000, rpmMin=1000, rpmMax=12000, power=500):
    #def __init__(self, feedMax=1000, rpmMin=1000, rpmMax=12000, power=500):

        #self.cncFeedMax = feedMax   # mm/min
        #self.cncRpmMin = rpmMin
        #self.cncRpmMax = rpmMax
        #self.cncPower = power       # in watts

        prefs = load_user_prefs()
        
        self.cncLimitsState = next(item for item in prefs if item["pref"] == "cncLimits").get("value")
        self.cncFeedMax = int(next(item for item in prefs if item["pref"] == "cncLimitFeedMax").get("value"))
        self.cncRpmMin  = int(next(item for item in prefs if item["pref"] == "cncLimitRpmMin").get("value"))
        self.cncRpmMax  = int(next(item for item in prefs if item["pref"] == "cncLimitRpmMax").get("value"))
        self.cncPower   = int(next(item for item in prefs if item["pref"] == "cncLimitPower").get("value"))
        # print(self.cncLimits, self.cncFeedMax, self.cncRpmMin, self.cncRpmMax, self.cncPower)


    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            print('\t\t---------------------')
            for k, v in items:
                #print(f"attribute: {k}    value: {v}")
                print(f"\t\tCNC_Limits.{k} = {v}")
            print('\t\t---------------------')

        return items


class FSCalculation:
    def __init__(self):

        # SS, chipload ...actually come as RANGE
        #     + even diff for HSM, REST maching
        #     + test cut vs finish vs rough vs v-carve vs chamfer vs ballend....
        # so are the ranges = test vs finish vs rough ENDMILLS doing >=50% woc?
        #       & then HSM, v-carve, chamfer etc etc all individual???
        # so how to represent (1. as data,
        #                     2 in gui AND for gui MOCK up condensed AND intro/guided/whatever version)
        # maybe indicate typical range (based on say required finish or roughing or..), then further reductions for test/?? and likely increases for HSM...
        #         PREPREPARE a section "Cutting Strategy" ...at least os placeholder/bookmark for above!!!

        # stickout
        # vibration/chatter
        #
        # more ops - review these not all = op??
        # v engrave, chamfer
        # ball end roughing/finishing....

        # Default or User settings, with defaults
        # E Machine efficiency
        # move C=feedFactor (ect??) here
        # overridden Vars ..hmmm possibly = final & also SOME are intermediate!!!
        # Pc Power Required at the cutter: Pg 1048
        # Kp
        # Q MRR

        # Flag hard to machine materials in each category (give alt/use that category)
        self.stockMaterial = None
        self.tool = Tool()

        #TODO should be in EACH tool & tool saved...
        self.toolWear = 1.1  # Tool Wear pg: 1048

        # Engagement
        self.WOC = self.tool.Diameter / 5   # TODO REFACTOR TO engageStepOver
        self.DOC = self.tool.Diameter       # TODO REFACTOR TO engageStepDown

        # Intermediate Outputs
        self.materials = load_materials()
        firstMaterialsRow = self.materials[0]
        self.stockMaterial = firstMaterialsRow["material"]

#Are these "extra" vars just for debugging or real use???
    #Have status/enable vars for override, CT & limits
    #....and SOME of the extra
        #,,,,inconsistent names
        #not ALL items have all vars - eg CL
        #CL also more unusual (ATM) as triggered by hFeed LIMIT...which changes CL...CT, the hFeed!!!
    #test#2 chip thinning AND overide calc
        #calc=>thinning=>limited=>overide
        #0.0990=>0.1004=>0.0990=>0.1004mm/tooth 
        # =========================================================
        self.surfaceSpeed = None

        # Chipload variables listed below in order of calculation & use

        # Chipload/fpt lookup based on Stock Material, Tool Material & dia
        # Then calculates CL = y_intercept + tdia * x_slope
        self.chiploadBase = None
        self.chipThinningEnabled = False 
        self.chipThinAdjusted = None
        # TODO REFACTOR above to  radialChipThinning & add axialChipThinning for ball end mills etc
        # chiploadLimited is used to limit hFeed, as it is driving input to calc hFeed
        self.chiploadLimited = None
        self.chiploadOverideFactor = 100    # 100% = no change
        self.chiploadOveriden = None
        self.chiploadForCalc = None
        
        # load user limits preferences, including if enabled by default
        self.limits = Cnc_limits()
        # =========================================================

        self.rpmBase = None
        self.rpmOverideValue = None
        self.rpmBeforeLimit = None
        self.rpmLimited = None
        self.rpmOveriden = None

        # Note cannot load FreeCAD ToolControllers here, 
        # so for init, just using default tool.
        # Engagement already set, so can get SS & CL
        self.updateSurfaceSpeed()
        self.updateChipload()
        # print("surfaceSpeed: ", self.surfaceSpeed, "chipload: ", self.chipload)
        
        # Outputs
        self.rpm = None
        self.hFeed = None   # mm/min
        self.vFeed = None   # mm/min
        self.millingPower = None   # Watts 
        self.drillingPower = 0.0   # Watts 

    # In case want to easily iterate ALL calc vars - eg to load/save a calculation!
    # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
    def attr_list(self, should_print=False):
        items = self.__dict__.items()
        if should_print:
            print('\t---------------------')
            for k, v in items:
                # skip dumping big materials csv content
                if k != "materials":
                    if k == "tool":
                        #print(f"attribute {k}    value: {v}")
                        self.tool.attr_list(should_print)
                    elif k == "limits":
                        #print(f"attribute {k}    value: {v}")
                        self.limits.attr_list(should_print)
                    else:
                        #print(f"attribute {k}    value: {v}")
                        print(f"\t{k} = {v}")
            print('\t---------------------')
        return items


    def printHeader(self):
        # header for console output
        print('material            woc  toolDia/F       rpm=>limit=>overide       cl   => thin =>limit =>overide         hfeed vfeed       Mill/DrillWatts')


    def printDetail(self):
        try:
            print(f'{self.stockMaterial:18} {float(self.WOC):2.2f} {self.tool.Diameter:2.2f}mm/{self.tool.Flutes:1f} {self.rpmBase:6.0f}=>{self.rpmLimited:6.0f}=>{self.rpm:6.0f}rpm {self.chiploadBase:1.4f}=>{self.chipThinAdjusted:1.4f}=>{self.chiploadLimited:1.4f}=>{self.chiploadForCalc:1.4f}mm/tooth {self.hFeed:5.0f} {self.vFeed:5.0f}mm/min {self.millingPower:5.0f}/{self.drillingPower:5.0f}', end = '')
            
            note = None
            note = next(item for item in self.materials if item["material"] == self.stockMaterial).get('notes') #get('material')
            if note != None:
                print(' -->', note)
            else:
                    print()

        except:
            print('printDetail failed,dumping vars')
            self.attr_list(True)


    def updateSurfaceSpeed(self):
        if self.stockMaterial:
            # TODO test behaviour in GUI here & just below for chipload!!!!
            ss_by_material = "ss_hss" if self.tool.Material == "HSS" else "ss_cbd"
            try:
                self.surfaceSpeed = next(item for item in self.materials if item["material"] == self.stockMaterial).get(ss_by_material)
                #print("Material", self.stockMaterial, "found ss:", self.surfaceSpeed)
            
            except StopIteration:
                self.surfaceSpeed = None
                #print("Material", self.stockMaterial, "found ss:", self.surfaceSpeed)
                print("Failed to find surfaceSpeed data for Stock Material: %s" % (self.stockMaterial))

        return "-"


    # TODO ???refactor & ditto SS??
    #   rename to lookup or calc or *update*
    #   ALSO do not return vars, direct save to self.XXX
    #   ?? extract MRR from calc & have similar update module??
    def updateChipload(self):
        """Calculate recommended chipload based on
            Stock & Tool Materials and Tool Diameter
            At present, ONLY providing a maximum value for Tool material either HSS or Carbide
            ie NOT providing a min-max range of CL values
        """

        if self.stockMaterial and self.tool.Material:
            # Determine which csv colum (ie dictionary keys) 
            # to lookup based on tool.Material
            if self.tool.Material == "HSS":
                cl_intercept_by_material = "cl_y_intercept_hss" 
                cl_slope_by_material = "cl_slope_hss" 
            else:
                cl_intercept_by_material = "cl_y_intercept_cbd"
                cl_slope_by_material = "cl_slope_cbd"

            try:
                max_y_intercept = next(item for item in self.materials if ((item["material"] == self.stockMaterial) )).get(cl_intercept_by_material)
                max_y_slope     = next(item for item in self.materials if ((item["material"] == self.stockMaterial) )).get(cl_slope_by_material)
                #print("ChipLoad y_intercept & slope: ", max_y_intercept, max_y_slope, self.tool.Diameter)
                #print("types: ", type(max_y_intercept), type(max_y_slope), type(self.tool.Diameter))
                if self.chiploadBase == None:
                    self.chiploadBase = max_y_intercept + self.tool.Diameter * max_y_slope
                
                if self.chiploadBase < 0.01:
                    self.chiploadBase = 0.01
                    print('\tFORCING chipload = 0.01, ie current minimum value for Power Constant C lookup')
                if self.chiploadBase > 5.0:
                    self.chiploadBase = 5.0
                    print('\tFORCING chipload = 5.0, ie current maximum value for Power Constant C lookup')
                
                self.chiploadForCalc = self.chiploadBase = max_y_intercept + self.tool.Diameter * max_y_slope
                
                # Chip Thinning
                # https://www.harveyperformance.com/in-the-loupe/combat-chip-thinning/
                # https://blog.tormach.com/chip-thinning-cut-aggressively
                #   "...hopefully thick enough to avoid rubbing"
                #    {other www say similar - so chip thinning is NOT a magic bullet!}
                #   "...increase your feedrate so that the actual chipload
                #    is equal to your (original recommended for 50% WOC) target"
                # https://shapeokoenthusiasts.gitbook.io/shapeoko-cnc-a-to-z/feeds-and-speeds-basics

                # ALWAYS calculate, other code decides if should use, ie if self.chipThinningEnabled and (self.WOC < 0.5 * self.tool.Diameter):
                if self.chipThinningEnabled and (self.WOC < 0.5 * self.tool.Diameter):
                    self.chipThinAdjusted = (self.tool.Diameter * self.chiploadForCalc)\
                        / (2 * math.sqrt((self.tool.Diameter * self.WOC) - (self.WOC * self.WOC)))
                else:
                    self.chipThinAdjusted = self.chiploadForCalc

                self.chiploadForCalc = self.chipThinAdjusted

                # Can reduce or increase = OK, BUT FIXME can be negative
                if self.chiploadOverideFactor != 100:
                    self.chiploadForCalc = self.chiploadOveriden = \
                        self.chiploadForCalc * float(self.chiploadOverideFactor) / 100
                else:
                    self.chiploadOveriden = self.chipThinAdjusted
                return
            
            except StopIteration:
                print("Failed to find Chipload data for Stock Material: %s & Tool Material: %s" % (self.stockMaterial, self.tool.Material))
                # sys.exit(1)
                return None

        return "-"


    def set_chiploadForCalc(self, chipload):
        self.chiploadForCalc = chipload


    def set_stockMaterial(self, material):
        self.stockMaterial = material


    def calculateRpm(self):
        if self.rpmBase == None:
            self.rpmBase = int((1000 * self.surfaceSpeed) / (math.pi * self.tool.Diameter))
        self.rpm = int((1000 * self.surfaceSpeed) / (math.pi * self.tool.Diameter))
        
        
    def calculateHfeed(self):
        self.hFeed = int(self.rpm * self.chiploadForCalc * self.tool.Flutes)
        
        
    def calculateMillingPower(self):
        Kp = next(item for item in self.materials if item["material"] == self.stockMaterial).get("kp")

        # Machine Efficiency: Pg 1049
        E = 0.80

        # TODO Have mapped power curve for Power Constant:
        # See "mc hb machining power p1057 table 2
        # feed factors for power const C.ods"
        # so can replace interp with equation
        # C = 0.785015843093532 * ChipLoad^-0.197425892437151
        # C = Power Constant
        # TODO: review p1057 MC HB & Kp & C
        # Kp =power constant (see Tables 1a and 1b)
        # C =feed factor for power constant (see Table 2)
        C = getInterpolatedValue(load_powerConstant(), self.chiploadForCalc, 'C, load_powerConstant(), self.chiploadForCalc')
        #print(" C", C,  "chipload ", self.chiploadForCalc, self.surfaceSpeed, self.tool.Diameter)
        
        # Calculation to Machineries Handbook: Pg 1058
        #print("WOC", self.WOC, " DOC", self.DOC, " Feed", self.hFeed, self.vFeed)
        # Material Removal Rate: Pg 1049
        Q = float((self.WOC * self.DOC * self.hFeed) / 60000)  # cm^3/s
        #print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", self.toolWear, " E", E, "chipload ", self.chiploadForCalc)
        
        # Power Required at the cutter: Pg 1048
        Pc = Kp * C * Q * self.toolWear

        # Milling Power Required at the motor
        Pm = 1000 * Pc / E
        # Convert to Hp
        #Hp = Pm * 1.341
        
        #print (Pc, Pm)
        self.millingPower = Pm        

 
    def calculateDrillingPower(self):
        # Machining Power
        # Kd = Work Material factor (Table 31) or is it  p1060 Table 6?
        # Ff = Feed factor (Table 33)
        # FM = Torque factor for drill diameter (Table 34)
        # A = Chisel edge factor for torque (Table 32)
        # w = Web thickness at drill point (See Table 32)

        # drilling power:
        Kd = next(item for item in self.materials if item["material"] == self.stockMaterial).get("Kd")
        Ff = getInterpolatedValue(load_feedFactor(), self.chiploadForCalc, 'Ff, load_feedFactor(), self.chiploadForCalc' )
        Fm = getInterpolatedValue(load_diameterFactors(), self.tool.Diameter, 'load_diameterFactors(), self.tool.Diameter')
        A = 1.085  # fixed value based on standard 118 deg drill. Table 32
        W = 0.18 * self.tool.Diameter  # fixed value based on standard 118 deg drill. Table 32

        M = Kd * Ff * Fm * A * W / 40000    # pg 1054
        self.drillingPower = Pc = M * self.rpm / 9550            # pg 1054
        
        
    def limitRpm(self):
        self.rpmBeforeLimit = None
        self.rpmLimited = self.rpmBase
        
        if self.limits.cncLimitsState == 'enabled':
            if self.rpm < self.limits.cncRpmMin:
                #print('\t', self.rpm, 'rpm is less than user set limit of ', limits.cncRpmMin)
                #print('\t', '\t', 'Below increases Surface speed, or YOU can reduce Tool Diameter')
                print('rpm lmt min-->', end = '')
                self.surfaceSpeed = self.surfaceSpeed * self.rpm / self.limits.cncRpmMin
                self.rpmBeforeLimit = self.rpm
                self.calculateRpm()
                self.rpmLimited = self.rpm
            elif self.rpm > self.limits.cncRpmMax:
                #print('\t', self.rpm, 'rpm is greater than user set limit of ', self.limits.cncRpmMax)
                #print('\t', '\t', 'Below reduces Surface speed, or YOU can increase Tool Diameter')
                print('rpm lmt max-->', end = '')
                self.surfaceSpeed = self.surfaceSpeed * self.limits.cncRpmMax / self.rpm
                self.rpmBeforeLimit = self.rpm
                self.calculateRpm()
                self.rpmLimited = self.rpm
        

    def limitHfeed(self):
        if self.limits.cncLimitsState == "enabled":
            if self.hFeed > self.limits.cncFeedMax:
                #print('\t', self.hFeed, 'mm/min is greater than user set limit of ', self.limits.cncFeedMax)
                #print('\t', '\t', 'Reduce Spindle speed, Surface speed, Chip Load or number of Tool Flutes')
                #print(self.chiploadForCalc, self.limits.cncFeedMax, self.hFeed)
                print(' feed lmt-->', end = '')
                
                # FIXME if chipthinning enabled AND WOC < Tool.dia / 2, then
                #   ??is chipThinning THEN going to reduce too CL much?
                self.chiploadLimited = self.chiploadForCalc * self.limits.cncFeedMax / self.hFeed
                self.chiploadForCalc = self.chiploadLimited
                
                self.calculateHfeed()
            else:
                self.chiploadLimited = self.chiploadBase
        else:
            self.chiploadLimited = self.chiploadBase
        

    def limitPwr(self):
        if self.limits.cncLimitsState == "enabled":
             if self.millingPower > self.limits.cncPower:
                #print('\t', self.millingPower, ' Watts currently required, but user set limit is ', self.limits.cncPower)
                #print('\t', '\t', 'Reduce either or both StepOver and StepDown to reduce Spindle Power required.')
                print(' pwr lmt-->', end = '')
                self.DOC = self.DOC * self.limits.cncPower / self.millingPower
                #self.updateSurfaceSpeed()
                self.updateChipload()
                self.calculateHfeed()
                self.calculateMillingPower()


    def calculate(self):

        """ 
        Relies on self.stockMaterial/Tool/WOC/DOC/chipLoad etc aready being up to date
        Other dependant vars, eg Kp, C etc, are looked up or defined below."""

        # clear initial outputs (ie before any overrides, limits or adjustments like chipthinning applied)
        self.rpmBase = None
        self.rpmLimited = None
        self.chiploadBase = None
        self.drillingPower = 0.0 
        self.millingPower = 0.0
        self.vFeed = 0.0

        # TODO Q? Do limits here, immed after calc related output, OR calc ALL outputs only here
        # then user can see "base outputs", then do a sep Limits /recalc for all outptus...
        # ...same Q for overrides .... maybe can do limits & overrides together?

        self.updateSurfaceSpeed()
        self.calculateRpm()
        self.limitRpm()
        if self.rpmOverideValue:
            if self.rpm > float(self.rpmOverideValue):
                self.rpmOveriden = float(self.rpmOverideValue)
                self.rpm = self.rpmOveriden
        
        # Horizontal Feed
        self.updateChipload()
        self.calculateHfeed()
        self.limitHfeed()

        if self.tool.tType == "endmill":
            # FIXME Vertical Feed this is simple milling (gives v fast), need vert & ramp AND also need drilling
            vFeed = int(self.chiploadForCalc * self.rpm)
            self.vFeed = vFeed 
            
            self.calculateMillingPower()
            self.limitPwr()
        elif self.tool.tType == "drill":
            # TODO drilling feed/rpm limit/s??
            self.calculateDrillingPower()
        
        #self.attr_list(True)
        self.printDetail()
        # print("power", Pc, Pm, Hp)

        return
