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
fsAddon.material = "Softwood"
#"Hard Plastics"  #"Hardwood"   # "Aluminium (6061)"

fsAddon.feedPerTooth = float(0.060)
fsAddon.WOC = 1.2
fsAddon.DOC = 6
fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
fsAddon.ss_by_material = "ss_cbd"           # "ss_hss" "ss_cbd"

# Original calculator behaviour, no SCRIPTED over rides
for dia in range(2,10,2):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
    #print("\t tool.toolDia %d rpm %d, feed %d, vfeed  %.d & Watts %d" % (tool.toolDia, rpm, feed, vfeed, Hp*745.6999))
#print(" -- end Feeds and Speeds **TEST** integration script/macro --")
