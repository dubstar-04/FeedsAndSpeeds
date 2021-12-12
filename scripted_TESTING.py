# Demonstration script to run an extended version of the Feed and Speed Calculator FreeCAD addon, 
# which can be installed from the "rpm_override" branch at https://github.com/spanner888/FeedsAndSpeeds/tree/rpm_override
#   Original code is https://github.com/dubstar-04/FeedsAndSpeeds

# This scripts demonstrates original Feed and Speed Calculator capability
# and also the added over ride limits set to match your CNC.

# version 1.0

import PathFeedsAndSpeeds
import math

fsAddon = PathFeedsAndSpeeds.FSCalculation()


#Skip rpm overide if rpm is < overide_value (eg stop say a 20mm endmill being overidden from 2000rpm to 10000rpm!)
fsAddon.rpm_overide_reduce_only = True

# Create some tool/endmill settings
tool = PathFeedsAndSpeeds.Tool()
tool.toolDia = 3.0
tool.flutes = 2
tool.material = 'HSS'   #'HSS';'carbide';'unknown'


fsAddon.WOC = tool.toolDia  # *.25
fsAddon.DOC = 1.0
fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"
fsAddon.material = "Aluminium (6061)"   #"Hardwood"   #Softwood"   #"Aluminium (6061)"


# Load user tool list
tools_sa = PathFeedsAndSpeeds.load_tools_standalone_only()
#print(tools_sa)

#header for console output
print('material            woc  toolDia calc=>thinning=>overide         rpm=>overide     hfeed vfeed       Watts')

fsAddon.calc_chip_thinning = False
print('test#1 original calc behaviour, no overides etc')
rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 


print('test#2 chip thinning AND overide calc')
fsAddon.chipload_overide = 50   #trying percentage reduction!!!!
fsAddon.calc_chip_thinning = True
tool.toolDia = 6.0
woclist = [6,5,4,3,2.5,2,1.5,1,0.8,0.6,0.4,0.2,0.1]
# or use a for loop
#for woc in range(int(tool.toolDia), 0, -1):
for woc in woclist:
    fsAddon.WOC = woc
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 

print('test#3 calc for a range of Tool diameters')
for dia in range(int(tool.toolDia-0),int(tool.toolDia+4),1):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 

print('test#4 Add rpm maximucm overide, change stock material and calc for a range of Tool diameters')
fsAddon.rpm_overide = 10000
fsAddon.material = "Softwood"
for dia in range(1,11,1):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
    #print("\t tool.toolDia %d rpm %d, feed %d, vfeed  %.d & Watts %d" % (tool.toolDia, rpm, feed, vfeed, Hp*745.6999))
#print('---------------------------')

print('test#5 change material again & calc for a range of Tool diameters')
fsAddon.material = "Aluminium (6061)"
for dia in range(1,11,1):
    tool.toolDia = dia
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 

#print(" -- end Feeds and Speeds **TEST** integration script/macro --")
