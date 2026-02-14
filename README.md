# FreeCAD Feeds and Speeds Calculator
A FreeCAD CAM Addon to help generate basic feeds and speeds for machining.  

## my Improvements:
### IMPORTANT:
do NOT "Auto-Load" the CAM/Path Workbench, or this Addon will NEVER Show in the Menue!!!

### 1st:
FC1.1 does not provide "BitShape" anymore, so the "Hack to detect Legacy-Tools" fires and prevent it from working propperly
as per the original programmer's comment, I commented-out the hack to disable it to make it work propperly!
maybe there are other ways to distinguish between legacy-tools ? but who really wants to use old FreeCAD-versions anymore?

### 2nd:
I noticed the Chipload can't be less than 0.02 which is sad for small tooling! so I analyzed the table with LibreOffice CALC,
and figured out it is Logarythmic!
Then manually added some values to keep a straight line in the Log.graph to 0.01, 0.005, 0.001 chipload



## Description
This addon when installed will appear in the CAM Workbench toolbar menu, the purpose of the addon is to define initial machining parameters
for the spindle speed and feedrate. This can be done by Spindle RPM or chipload (Feed Per Tooth).

## Features
* Select tool controller
* Select workpiece material
* Select tool material
* Set machining parameters
* Write calculated feedrate and spindle speed to the selected tool controller
 
## Requirements
* FreeCAD v 1.0 or later
* CAM Toolbit (Legacy tools not supported)
* Python3  
* Qt5

## Installation
1. Use `git clone` or download the `.zip` file of this repo directly in to your [FreeCAD `Mod/` directory](https://www.freecadweb.org/wiki/Installing_more_workbenches).  
2. Restart FreeCAD 

## Feedback  
If you have feedback or need to report bugs please participate on the related [CAM Forum](https://forum.freecadweb.org/viewforum.php?f=15). 

## Disclaimer
This is an experimental tool and must be used at your own risk. Machine tools are dangerous and the author of this tool will not be responsible for any 
damage or personal injury caused by using incorrect machining parameters.
