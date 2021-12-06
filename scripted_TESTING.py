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
# ONLY have matching "Softwood" &  "Aluminium (6061)" ATM
#fsAddon.material = "Softwood"
fsAddon.material = "Aluminium (6061)"
#"Hard Plastics"  #"Hardwood"   # "Aluminium (6061)"

#fsAddon.feedPerTooth = float(0.060)
#fsAddon.WOC = 1.2
#fsAddon.DOC = 6
#fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
#fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"

fsAddon.WOC = tool.toolDia
fsAddon.DOC = 1.3
fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
#fsAddon.ss_by_material = "ss_cbd"           # "ss_hss" "ss_cbd"
fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"

# Original calculator behaviour WITH overides !!!!!!!
# >>>>>>these are GOOD way to do overides!!!!!!!!
#   even with BOTH overides above - still getting "FAST" hfeeds >>>>YES HAD fsAddon.ss_by_material = "ss_cbd" INSTEAD OF: ss_hss!!!!!!!
# vibration work: /home/spanner888/Documents/Hobby/Projects/vibration/_hackaday Ard Nano adxl335 accelerometer fft/fftAnal_s888/3_axis/Python_35/
#>>>>>>BUT WHERE is feeds & speeds & woc/doc info??? ...sep garage txt file??

#CNC Mills, Drills, Collets & Reamers v1.3


fsAddon.rpm_overide = 10000
#fsAddon.chipload_overide = 60   #trying percentage reduction!!!!
#TODO overrides CAN lead to increasesd...ie not just reductions!!!
# add a flag to dis/allow ...ONE FLAG for each overide ie rpm, chipload....
# from spreadsheet ...somebody suggested:
# Suggestion is to start/TEST at HALF calculated ideal feed rate	<<<< which is same as reducing chpload/fpt by half (update 2021-12)
#   Feed rate based on chip thickness (chip load).ods


# REMEMBER HAVE *NOT* MATCHED MY MAT_GROUPS WITH EXISTING MATERIALS GROUPS!!!!!!!
# ONLY have matching "Softwood" &  "Aluminium (6061)" ATM
# Optional print header for output
print('material           toolDia calc_cl=>overide          rpm=>overide    hfeed vfeed       Hp')
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
