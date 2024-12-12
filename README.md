# FreeCAD Feeds and Speeds Calculator
A FreeCAD CAM Addon to help generate basic feeds and speeds for machining.  

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
