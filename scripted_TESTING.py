# Demonstration script to run Feed and Speed Calculator FreeCAD addon.
# This release: ???????? UDATE THIS!!!!!!!<<<<<<<<<<<
# original release: https://github.com/spanner888/FeedsAndSpeeds/tree/rpm_override
# Original code is https://github.com/dubstar-04/FeedsAndSpeeds

# Demonstrates original Feed and Speed Calculator capability, chipthining
# and also the added over ride limits set to match your CNC.

# version 1.0

import PathFeedsAndSpeeds
# import math

def calcAttribs():
    print('example of all calc attribs - eg to load/save a calculation')
    fsAddon.attr_list(True)

    print('----------------------------------------')
    print('Can also access dictionary directly')
    items = fsAddon.__dict__.items()
    [print(f"attribute: {k}    value: {v}") for k, v in items]
    print('----------------------------------------')


    for key, value in fsAddon.__dict__.items():
        if type(value) is dict:
            print('\t>>>dict: ', key)
            val_items = value.__dict__.items()
            [print(f"attribute: {k}    value: {v}") for k, v in val_items]
        else:
            print(key, '\t', value)
    print('----------------------------------------')
    for key, value in fsAddon.__dict__.items():
        # can't tell if dict'      'maybe just try/except???'
        # if type(value) is metaclass:
        try:
            for key1, value1 in value.__dict__.items():
                [print(f"{k}    {v}") for k, v in value1]
        except:
            pass
        # print(key, '\t', value, type(value))
        # print(key, '\t', value)
    print('----------------------------------------')


    try :
        import __builtin__
    except:
        # Python 3.x
        import builtins

    try :
        builtin_types = [t for t in __builtin__.__dict__.itervalues() if isinstance(t, type)]
    except:
        builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]

    # below part of exploring load/save entire calculations...not working atm.
    #for key, value in fsAddon.__dict__.items():
        #if type(value) is builtin_types:
            #print(key, '\t', value, type(value))
            #print(key, '\t', value)
        #else:
            #print('else')
            #for key1, value1 in value.__dict__.items():
                #[print(f"{k}    {v}") for k, v in value1]


fsAddon = PathFeedsAndSpeeds.FSCalculation()
print("..................")

#Create some tool/endmill settings FOR SUTTON TEST DATA - so material names different!!!!!!!
#fsAddon.tool.Diameter = 5.0
#fsAddon.tool.Flutes = 1
#fsAddon.tool.Material = 'HSS'   # 'HSS';'Carbide';'unknown'
#fsAddon.WOC = fsAddon.tool.Diameter  / 5
#fsAddon.DOC = 1.0
#fsAddon.toolWear = 1.1                      # Tool Wear pg: 1048
#fsAddon.stockMaterial = "N_21_Aluminum & Magnesium  - wrought alloy"
#fsAddon.chipThinningEnabled = False
#fsAddon.limits.cncLimitsState = 'anything except enabled'

#print('test SUTTON = dif materials!!!')
#fsAddon.printHeader()
#fsAddon.calculate()

#fsAddon.stockMaterial = "N_22_Aluminum & Magnesium  - wrought alloy"
#fsAddon.calculate()
#exit()



# Create some tool/endmill settings
#tool = PathFeedsAndSpeeds.Tool()
fsAddon.tool.Diameter = 3.0
fsAddon.tool.Flutes = 2
fsAddon.tool.Material = 'HSS'   # 'HSS';'Carbide';'unknown'

fsAddon.WOC = fsAddon.tool.Diameter  / 5
fsAddon.DOC = 1.0
fsAddon.toolWear = 1.1                      # Tool Wear pg: 1048
# fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"
# "Hardwood"   #Softwood"   #"Aluminium (6061)"
fsAddon.stockMaterial = "Aluminium (6061)"
#print("ss: ", fsAddon.surfaceSpeed, "self.chiploadBase", fsAddon.chiploadBase)


#so now create/read limits THEN USE THEM TO CHANGE outputs
#...print nicely showing changes
#limits = PathFeedsAndSpeeds.Cnc_limits()
#limits.attr_list(True)

#limits
fsAddon.chipThinningEnabled = False
fsAddon.limits.cncLimitsState = 'anything except enabled'

print()
print()

#fsAddon.attr_list(True)
#fsAddon.limits.attr_list(True)

print('test#1 Standard calc behaviour, no overides or limits')
fsAddon.printHeader()
#print('printDetail crash that will appear on next line DUE TO TRYING USE IT BEFORE VARS ALL SET!!!!')
#fsAddon.printDetail()
fsAddon.calculate()
# Just for debug - True = print all fsAddon self.variables
#fsAddon.attr_list(True)

print('test#1A ditto, but tool material changed to give diff chipload')
fsAddon.tool.Material = 'Carbide'
fsAddon.calculate()
#fsAddon.attr_list(True)


#exit()



print()
print()
print('test#2 chip thinning AND overide calc')
fsAddon.tool.tType = 'drill'
fsAddon.chipload_overide = 50   # trying percentage reduction!!!!
fsAddon.chipThinningEnabled = True
fsAddon.tool.Diameter = 6.0
woclist = [6, 5, 4, 3, 2.5, 2, 1.5, 1, 0.8, 0.6, 0.4, 0.2, 0.1]
# or use a for loop
# for woc in range(int(fsAddon.tool.toolDia), 0, -1):
for woc in woclist:
	fsAddon.WOC = woc
	fsAddon.calculate()

print()
print()
print('test#3 calc for a range of Tool diameters')
fsAddon.tool.tType = 'endmill'
for dia in range(int(fsAddon.tool.Diameter - 0), int(fsAddon.tool.Diameter + 4), 1):
	fsAddon.tool.Diameter = dia
	fsAddon.calculate()
	
print()
print()
print('test#4 Add rpm maximum overide, change stock material and calc for a range of Tool diameters')
# NB set = None to stop rpm override!!!!
fsAddon.rpmOverideValue = 10000
fsAddon.stockMaterial = "Softwood"

for dia in range(1, 11, 1):
	fsAddon.tool.Diameter = dia
	fsAddon.calculate()
	# print("\t fsAddon.tool.Diameter %d rpm %d, feed %d, vfeed  %.d & Watts %d" % (fsAddon.tool.Diameter, rpm, feed, vfeed, Hp*745.6999))
# print('---------------------------')

print()
print()
print('test#5 change material again & calc for a range of Tool diameters')
fsAddon.stockMaterial = "Aluminium (6061)"

# fixed value so check chipthinning kicks in at correct tool.dia/woc
fsAddon.WOC = 2.0
for dia in range(3, 16, 1):
	fsAddon.tool.Diameter = dia
	fsAddon.calculate()


#exit()

print()
print()
print()
print('test#6 change material again & calc for a range of Tool diameters')
print('  AND enforce cnc limits read from prefs.csv,')
print('  BUT only if cncLimits, enabled: ')
#fsAddon.limits.cncLimitsState = 'anything except enabled'
fsAddon.limits.cncLimitsState = 'enabled'
#fsAddon.limits.attr_list(True)

# remove all overrides (usually each one user based via gui) for limit testing
fsAddon.chiploadOverideFactor = 100
fsAddon.chipThinningEnabled = False
fsAddon.rpmOverideValue = None

fsAddon.stockMaterial = "Aluminium (6061)"
for dia in range(1, 16, 1):
	fsAddon.tool.Diameter = dia
	fsAddon.WOC = dia / 2
	fsAddon.DOC = dia / 2
	#print("Tool dia = ", dia, ' : ', end = '') 
	fsAddon.calculate()
