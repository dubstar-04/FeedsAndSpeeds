# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import math
from bisect import bisect_right
import sys

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


def getInterpolatedValue(inputDict, value):
    keys = list(inputDict.keys())
    values = list(inputDict.values())
    interpolation = Interpolate(keys, values)
    try:
        return interpolation(value)
    except:
        #TODO should pass in & print here WHICH var was looking up!!!!
        print("Interpolated value outside the expected range")
        return None


def load_powerConstant():
    powerConstant = {
        # Constant Power
        # Data from Machineries Handbook 28.
        # Table 2
        # mm/tooth : C
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
            1.50: 0.72  # noqa: E131
        }

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

    # ss_hss = surface speed (m/min) for milling with high speed steel tools (hss)
    # ss_cbd = surface speed (m/min) for milling with carbide tools
    # ss_drill_hss = surface speed (m/min) for drilling with high speed steel tools (hss)
    # ss_drill_cbd = surface speed (m/min) for drilling with carbide tools
    # Kd = workMaterialFactor from Table 31
    # ref: 1 ft/min = 0.3048 m/min

    return load_data('materials_ss_cl.csv')


def load_tools_standalone_only():
    return load_data('tools_standalone_only.csv')

# --- csv -----------------------------
# From user imm https://forum.freecadweb.org/viewtopic.php?f=15&t=59856&start=50
import csv
# -- any numeric value that can be converted to float is converted to float.
def fitem(item):
    item.strip()
    try:
        item=float(item)
    except ValueError:
        pass
    return item

# -- takes a header list and row list converts it into a dict. Numeric values converted to float in the row list wherever possible. 
def rowConvert(h,a):
    b=[]
    for x in a:
        b.append(fitem(x))
    k = iter(h)
    it = iter(b)
    res_dct = dict(zip(k, it))
    return res_dct


def load_data(dataFile):
    import os
    p = os.path.dirname(__file__)
    #TODO windows path '\' ???
    filename = p + '/' + dataFile

    dataDict=[]
    with open(filename,'r') as csvin:
        alist=list(csv.reader(csvin))
        firstLine = True
        for a in alist:
            if firstLine:
                if len(a) == 0: continue
                if len(a) == 1: continue
                else:
                    h = a
                    firstLine = False
            else:
                # print(rowConvert(h,a))
                dataDict.append(rowConvert(h,a))

    return dataDict
# --- end csv -----------------------------

class Tool:
    def __init__(self, toolDia=6, flutes=3, material='HSS'):
        self.toolDia = toolDia
        self.flutes = flutes
        self.material = material


class Cnc_limits:
    """ Define limits of your machines feed rate, rp, and power
        Defaults are low to help test over rides & also are for my low end home made CNC"""

    def __init__(self, feedMax=1000, rpmMin=1000, rpmMax=12000, power=500):

        self.cncFeedMax = feedMax   # mm/min
        self.cncRpmMin = rpmMin
        self.cncRpmMax = rpmMax
        self.cncPower = power       # in watts


class FSCalculation:
    def __init__(self):

        self.material = None
        self.rpm_overide = None
        self.rpm_overide_reduce_only = False
        self.chipload_overide = None
        self.ss_by_material = None
        
        # Chipload (fpt) is table lookup based on Stock material, Tool Material and Tool dia
        # Then calculates CL = y_inercept + tdia*x_slope
        self.cl_by_mat_tdia_tmat = None
        #self.feedPerTooth = None
        self.calc_chip_thinning = False
        self.toolWear = None
        self.WOC = None
        self.DOC = None
        self.limits = None

    def get_surface_speed(self):
        #print("material", self.material)
        if self.material:
            
            #TODO test behaviour in GUI here & just below for chipload!!!!
            # MAYBE just print msg & DO NOT exit ....similar behaviour to interp method...although then later a calc can crash!!
            try:
                materials = load_materials()
                surfaceSpeed = next(item for item in materials if item["material"] == self.material).get(self.ss_by_material)
                #print("material", self.material, "found ss:", surfaceSpeed)
                return surfaceSpeed
            except:
                print("Failed to find surfaceSpeed data for Stock material: %s" % (self.material))

        return "-"

    def get_chipload(self, tool):
        '''Calculate recommended chipload based Stock & Tool materials and Tool Diameter
            At present, just providing a maximum value.
        '''
        if self.material:
            if tool.material:
                materials = load_materials()
                #print(materials)
                #print(next(item for item in materials))
                #TODO test behaviour in GUI here & just below for chipload!!!!
                # MAYBE just print msg & DO NOT exit ....similar behaviour to interp method...although then later a calc can crash!!
                try:
                    #mat group
                    max_y_intercept = next(item for item in materials if ((item["material"] == self.material) and (item["tool_material"] == tool.material))).get("max_b0_y_intercept")
                    max_y_slope = next(item for item in materials if ((item["material"] == self.material) and (item["tool_material"] == tool.material))).get("max_b1_slope")
                    #print('chipload data', max_y_intercept, max_y_slope, tool.toolDia, tool.material)
                    chipload = max_y_intercept + tool.toolDia*max_y_slope
                    #print('calculated chipload ', max_y_intercept, max_y_slope, tool.toolDia, tool.material, chipload)
                    return chipload
                except:
                    print("Failed to find Chipload data for Stock material: %s & Tool material: %s" % (self.material, tool.material))
                    #sys.exit(1)
                    return None

        return "-"

    def set_material(self, material):
        self.material = material

    def calculate(self, tool, surfaceSpeed):

        materials = load_materials()
        #print(materials)
        # ACTUALLY SS IS BEING PASSED IN ...so no need for >>>pull request #18 in queue as at 2021-12-05 to re-enable next line!!
        #surfaceSpeed = self.get_surface_speed()
        
        calc_chipload = self.get_chipload(tool)
        # intermediate/temp values used to show flow/effects of chip thinning adjustment &/or chip thinning overide
        orig_chipload = calc_chipload
        calc_chipload_chip_thin_adjusted = calc_chipload
        
        # https://www.harveyperformance.com/in-the-loupe/combat-chip-thinning/
        # https://blog.tormach.com/chip-thinning-cut-aggressively
        #   "...hopefully thick enough to avoid rubbing"    {other www say similar - so chip thinning is NOT a magic bullet!}
        #   "...increase your feedrate so that the actual chipload is equal to your (original recommended for 50% WOC) target"
        # https://shapeokoenthusiasts.gitbook.io/shapeoko-cnc-a-to-z/feeds-and-speeds-basics
        if self.calc_chip_thinning and (self.WOC < 0.5 *  tool.toolDia):
            #TODO what about when WOC gets small, then calc_chipload_chip_thin_adjusted is GREATER than WOC!!!!
            #>>>># above is prob INCORRECT, as WOC gets small, the chip thinning diag show shallow cut, but APPROX view is????
            # ...or just one of MANY vars/parts of this calculator where "extreme" situations/settings/values produce "unreliable" results!
            # eg extremely large or small dia tool bits => chipload, load_powerConstant if chipload < 0.02 or > 1.5 
            # Extreme overides of SS or chipload also will casue issues.
            # ....so doco as general advice ....better if have warnigns in danger settings/vars....
            calc_chipload_chip_thin_adjusted = (tool.toolDia * calc_chipload) / ( 2 *math.sqrt((tool.toolDia * self.WOC) - (self.WOC*self.WOC)))
            #print(tool.toolDia, self.WOC, calc_chipload , ' --> ', calc_chipload_chip_thin_adjusted)
            calc_chipload = calc_chipload_chip_thin_adjusted

        if self.chipload_overide:
            #print ('\t\t\t\t\tv ATM chip thinning overides, the chipload overide value!!! ...oops???')
            #print("calc_chipload", calc_chipload, ' to ', calc_chipload * float(self.chipload_overide) / 100)
            chipload_overide = calc_chipload * float(self.chipload_overide) / 100
            calc_chipload = chipload_overide
        #TODO should above chipload chip thinning "overide" & chipload_overide be merged??

        Kp = next(item for item in materials if item["material"] == self.material).get("kp")
        
        #TODO Have mapped power curve for Power Constant: See "mc hb machining power p1057 table 2 feed factors for power const C.ods"
        #       ...so can replace interp with equation C = 0.785015843093532 * ChipLoad^-0.197425892437151 (^ = raised to power of..)
        #               above #s for metric. Curve fit look v good, but smaller ChipLoad are gunna be less accurate
        #                   1. curve goes up v v sharp for small vaules, so small varations = larger error
        #                   2. chip thinning & min possible chip thickness...
        # C = Power Constant
        C = getInterpolatedValue(load_powerConstant(), calc_chipload)    #self.feedPerTooth)
        rpm = int((1000 * surfaceSpeed) / (math.pi * tool.toolDia))
        calc_rpm = rpm

        if self.rpm_overide:
            if calc_rpm > float(self.rpm_overide) and self.rpm_overide_reduce_only:
                #Avoid faster rpm than calculated. Esp for larger dia tools eg 20mm, not likely to want 3,000rpm->10000rpm!!!
                #TODO does this need to be an option, or message to user???
                #    ...maybe coloured warning highlight of overide field????
                #TODO also what about ss & cl overides - similar issue(s)?
                calc_rpm = float(self.rpm_overide)
            if not self.rpm_overide_reduce_only:
                # Force overide if user has not enabled rpm_overide_reduce_only, might reduce, or might increase rpm.
                calc_rpm = float(self.rpm_overide)

        # Machine Efficiency: Pg 1049
        E = 0.80

        # Machining Power
        # Horizontal Feed
        #hfeed = int(calc_rpm * self.feedPerTooth * tool.flutes)
        hfeed = int(calc_rpm * calc_chipload * tool.flutes)
        # Calculation to Machineries Handbook: Pg 1058
        # print("WOC", self.WOC, " DOC", self.DOC, " Feed", feed)
        # Material Removal Rate: Pg 1049
        Q = float((self.WOC * self.DOC * hfeed) / 60000)  # cm^3/s
        #print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", self.toolWear, " E", E)
        # Power Required at the cutter: Pg 1048
        Pc = Kp * C * Q * self.toolWear

        # Vertical Feed
        #vfeed = int(self.feedPerTooth * calc_rpm)
        vfeed = int(calc_chipload * calc_rpm)
        # Kd = Work material factor (Table 31)
        # Ff = Feed factor (Table 33)
        # FM = Torque factor for drill diameter (Table 34)
        # A = Chisel edge factor for torque (Table 32)
        # w = Web thickness at drill point (See Table 32)

        # TODO: Re-enable drilling power
        # drilling power:
        # Kd = next(item for item in materials if item["material"] == self.material).get("Kd")
        # Ff = getInterpolatedValue(load_feedFactor(), self.feedPerTooth)
        # Fm = getInterpolatedValue(load_diameterFactors(), tool.toolDia)
        # A = 1.085  # fixed value based on standard 118 deg drill. Table 32
        # W = 0.18 * tool.toolDia  # fixed value based on standard 118 deg drill. Table 32

        # M = Kd * Ff * Fm * A * W / 40000    # pg 1054
        # Pc = M * calc_rpm / 9550            # pg 1054

        # Power Required at the motor
        Pm = Pc / E
        # Convert to Hp
        Hp = Pm * 1.341

        print(f'{self.material:18} {self.WOC:2.2f} {tool.toolDia:2.2f}mm {orig_chipload:1.4f}=>{calc_chipload_chip_thin_adjusted:1.4f}=>{calc_chipload:1.4f}mm/tooth {rpm:6.0f}=>{calc_rpm:6.0f}rpm {hfeed:5.0f} {vfeed:5.0f}mm/min {Hp*745.6999:5.0f}W')
        # print("power", Pc, Pm, Hp)
        return calc_rpm, hfeed, vfeed, Hp
