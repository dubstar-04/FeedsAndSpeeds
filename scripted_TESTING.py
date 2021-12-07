# Demonstration script to run an extended version of the Feed and Speed Calculator FreeCAD addon, 
# which can be installed from the "rpm_override" branch at https://github.com/spanner888/FeedsAndSpeeds/tree/rpm_override
#   Original code is https://github.com/dubstar-04/FeedsAndSpeeds

# This scripts demonstrates original Feed and Speed Calculator capability
# and also the added over ride limits set to match your CNC.

# version 1.0

import PathFeedsAndSpeeds
import math

fsAddon = PathFeedsAndSpeeds.FSCalculation()

# REMEMBER HAVE *NOT* MATCHED MY MAT_GROUPS WITH EXISTING MATERIALS GROUPS!!!!!!!
# ONLY have matching "Softwood" &  "Aluminium (6061)" ATM
#fsAddon.material = "Softwood"
fsAddon.material = "Aluminium (6061)"
#"Hard Plastics"  #"Hardwood"   # "Aluminium (6061)"

#fsAddon.feedPerTooth = float(0.060)

# setting to match job: DSG12H leadnut block_vD_002_faster_Job.ngc  see #CNC Mills, Drills, Collets & Reamers v1.3
# feed results still 680 & 480 @60% chipload reduction (& min chipload slope & using HSS tool, not carbide)
# ...but getting to ball park
#tool = PathFeedsAndSpeeds.Tool()
#tool.toolDia = 4.0
#tool.flutes = 1
#fsAddon.WOC = tool.toolDia
#fsAddon.DOC = 1.3
#fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
#fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"
#fsAddon.rpm_overide = 10000
#fsAddon.chipload_overide = 60   #trying percentage reduction!!!!
#fsAddon.material = "Aluminium (6061)"

# setting to match job: Dust_extractor_ring_#a1_001_0.FCStd see #CNC Mills, Drills, Collets & Reamers v1.3
tool = PathFeedsAndSpeeds.Tool()
tool.toolDia = 3.0
tool.flutes = 2
tool.material = 'HSS'   #'HSS';'carbide';'unknown'

fsAddon.WOC = tool.toolDia  # *.25
#print('fsAddon.WOC', fsAddon.WOC, ' = ', 100*fsAddon.WOC/tool.toolDia, '% for chip thinning adjustment')
fsAddon.DOC = 1.0
fsAddon.toolWear = 1.1                      ## Tool Wear pg: 1048
fsAddon.ss_by_material = "ss_hss"           # "ss_hss" "ss_cbd"
fsAddon.rpm_overide = 10000
fsAddon.chipload_overide = 25   #trying percentage reduction!!!!
print('fsAddon.chipload_overide = 25 ')
fsAddon.material = "Aluminium (6061)"   #"Hardwood"   #Softwood"   #"Aluminium (6061)"

# test#1 chip thinning calc
tool.toolDia = 10.0
calc_chipload = 0.01
print('material           toolDia calc_cl=>overide          rpm=>overide    hfeed vfeed       Hp')
for woc in range(int(tool.toolDia), 0, -1):
    fsAddon.WOC = woc
    rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
    #if woc < 0.5 *  tool.toolDia:
        #calc_chipload_chip_thin_adjusted = (tool.toolDia * calc_chipload) / ( 2 *math.sqrt((tool.toolDia * fsAddon.WOC) - (fsAddon.WOC*fsAddon.WOC)))
        #print("%2.4f %2.4f --> %2.4f " % (woc, calc_chipload , calc_chipload_chip_thin_adjusted))
        #calc_chipload = calc_chipload_chip_thin_adjusted
        #rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 


# Original calculator behaviour WITH overides !!!!!!!
# >>>>>>these are GOOD way to do overides!!!!!!!!
#   even with BOTH overides above - still getting "FAST" hfeeds >>>>YES HAD fsAddon.ss_by_material = "ss_cbd" INSTEAD OF: ss_hss!!!!!!!
# vibration work: /home/spanner888/Documents/Hobby/Projects/vibration/_hackaday Ard Nano adxl335 accelerometer fft/fftAnal_s888/3_axis/Python_35/
#>>>>>>BUT WHERE is feeds & speeds & woc/doc info??? ...sep garage txt file??

#TODO overrides CAN lead to increasesd...ie not just reductions!!!
# add a flag to dis/allow ...ONE FLAG for each overide ie rpm, chipload....
# from spreadsheet ...somebody suggested:
# Suggestion is to start/TEST at HALF calculated ideal feed rate	<<<< which is same as reducing chpload/fpt by half (update 2021-12)
#        Feed rate based on chip thickness (chip load).ods

# REMEMBER HAVE *NOT* MATCHED MY MAT_GROUPS WITH EXISTING MATERIALS GROUPS!!!!!!!
# ONLY have matching "Softwood" &  "Aluminium (6061)" ATM
# Optional print header for output

#print('material           toolDia calc_cl=>overide          rpm=>overide    hfeed vfeed       Hp')
#rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
#for dia in range(int(tool.toolDia-0),int(tool.toolDia+4),1):
    #tool.toolDia = dia
    #rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 


#fsAddon.material = "Softwood"
#for dia in range(1,11,1):
    #tool.toolDia = dia
    #rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
    #print("\t tool.toolDia %d rpm %d, feed %d, vfeed  %.d & Watts %d" % (tool.toolDia, rpm, feed, vfeed, Hp*745.6999))
#print('---------------------------')
#fsAddon.material = "Aluminium (6061)"
#for dia in range(1,11,1):
    #tool.toolDia = dia
    #rpm, feed, vfeed, Hp = fsAddon.calculate(tool, fsAddon.get_surface_speed()) 
#print(" -- end Feeds and Speeds **TEST** integration script/macro --")
