# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the Feeds & Speeds addon.

# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import math
from bisect import bisect_right

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
        # print("Interpolated value outside the expected range")
        return None


def load_powerConstant():
    powerConstant = {
        # Constant Power
        # Data from Machineries Handbook 28.
        # Table 2
        # mm/tooth : C
            0.001: 2.8, # Logarythmic "guestimation"
            0.005: 2.2, # just look the values in LibreOffice CALC X-Y graph
            0.01: 1.95, # and make axis with 1st numbers Logarythmic = pretty straight line!

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
    # Diameter Factors
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


class Tool:
    def __init__(self, toolDia=6, flutes=3):

        self.toolDia = toolDia
        self.flutes = flutes

class FSCalculation:
    def __init__(self):

        self.material = None
        self.rpm_overide = None
        self.toolWear = None
        self.feedPerTooth = None
        self.WOC = None
        self.DOC = None

    def set_material(self, material):
        self.material = material

    def calculate(self, tool, surfaceSpeed):

        # materials = load_materials()
        Kp = float(self.material.get("Kp"))
        # C = Power Constant
        C = getInterpolatedValue(load_powerConstant(), self.feedPerTooth)
        rpm = int((1000 * surfaceSpeed) / (math.pi * tool.toolDia))
        calc_rpm = rpm

        if self.rpm_overide:
            calc_rpm = float(self.rpm_overide)

        # Machine Efficiency: Pg 1049
        E = 0.80

        # Machining Power
        # Horizontal Feed
        hfeed = int(calc_rpm * self.feedPerTooth * tool.flutes)
        # Calculation to Machineries Handbook: Pg 1058
        if C is not None:
            # print("WOC", self.WOC, " DOC", self.DOC, " Feed", feed)
            # Material Removal Rate: Pg 1049
            Q = float((self.WOC * self.DOC * hfeed) / 60000)  # cm^3/s
            # print("Kp", Kp, " C", C,  " Q", round(Q * 60, 2), " W", self.toolWear, " E", E)
            # Power Required at the cutter: Pg 1048
            Pc = Kp * C * Q * self.toolWear

        # Vertical Feed
        vfeed = int(self.feedPerTooth * calc_rpm)
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

        Hp = None
        if C is not None:
            # Power Required at the motor
            Pm = Pc / E
            # Convert to Hp
            Hp = Pm * 1.341

        # print("power", Pc, Pm, Hp)
        return calc_rpm, hfeed, vfeed, Hp
