# FreeCAD Feeds and Speeds Calculator
A FreeCAD Path Addon to help generate basic feeds and speeds for machining.  

## Description
This addon when installed will appear in the Path Workbench toolbar menu, the purpose of the addon is to define initial machining parameters
for the spindle speed and feedrate. This can be done by Spindle RPM or chipload (Feed Per Tooth).

## Features
* Select workpiece material
* Select Tool Material
* Set machining parameters
* Scripting only features (not yet added to GUI)
 * Ability to automaticaly over ride outputs to limits set to match your CNC.
 * Optional print of all inputs
 * Script example included in examples directory
 
## Requirements
* FreeCAD v0.19  
* Python3  
* Qt5

## Installation
1. Use `git clone` or download the `.zip` file of this repo directly in to your [FreeCAD `Mod/` directory](https://www.freecadweb.org/wiki/Installing_more_workbenches).  
2. Restart FreeCAD 

## Feedback  
If you have feedback or need to report bugs please participate on the related [Path Forum](https://forum.freecadweb.org/viewforum.php?f=15). 

## Disclaimer
This is an experimental tool and must be used at your own risk. Machine tools are dangerous and the author of this tool will not be responsible for any 
damage or personal injury caused by using incorrect machining parameters.
