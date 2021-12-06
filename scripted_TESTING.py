# Demonstration script to run an extended version of the Feed and Speed Calculator FreeCAD addon, 
# which can be installed from the "rpm_override" branch at https://github.com/spanner888/FeedsAndSpeeds/tree/rpm_override
#   Original code is https://github.com/dubstar-04/FeedsAndSpeeds

# This scripts demonstrates original Feed and Speed Calculator capability
# and also the added over ride limits set to match your CNC.

# version 1.0

import PathFeedsAndSpeeds

fsAddon = PathFeedsAndSpeeds.FSCalculation()

# set some values to suit your needs
# Some examples:-
tool = PathFeedsAndSpeeds.Tool()
tool.toolDia = 4.0
tool.flutes = 1



# REMEMBER HAVE *NOT* MATCHED MY MAT_GROUPS WITH EXISTING MATERIALS GROUPS!!!!!!!
# ONLY *one* matching Softwood ATM
#fsAddon.material = "Softwood"
fsAddon.material = "Aluminium (6061)"
#"Hard Plastics"  #"Hardwood"   # "Aluminium (6061)"

fsAddon.feedPerTooth = float(0.060)
fsAddon.WOC = 1.2
fsAddon.DOC = 6
fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
fsAddon.ss_by_material = "ss_cbd"           # "ss_hss" "ss_cbd"


# >>>>>>these are GOOD way to do overides!!!!!!!!
fsAddon.rpm_overide = 9000
fsAddon.chipload_overide = 60   #trying percentage reduction!!!!
# from spreadsheet ...somebody suggested:
# Suggestion is to start/TEST at HALF calculated ideal feed rate	<<<< which is same as reducing chpload/fpt by half (update 2021-12)
#   Feed rate based on chip thickness (chip load).ods

# even with BOTH overides above - still getting "FAST" hfeeds
# review my recent test settings ...reduce rpm/feed further?????????????????



# Original calculator behaviour, no SCRIPTED over rides
fsAddon.material = "Softwood"
for dia in range(1,11,1):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
    #print("\t tool.toolDia %d rpm %d, feed %d, vfeed  %.d & Watts %d" % (tool.toolDia, rpm, feed, vfeed, Hp*745.6999))
print('---------------------------')
fsAddon.material = "Aluminium (6061)"
for dia in range(1,11,1):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
#print(" -- end Feeds and Speeds **TEST** integration script/macro --")
