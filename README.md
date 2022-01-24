# Feeds and Speeds Calculator
A Calculator to help generate basic feeds and speeds for machining.

## Description
This calculator is an aid to defining initial machining parameters
for the spindle speed, feedrates and power.
When installed in FreeCAD, this addon will appear in the Path Workbench toolbar menu.

Calculator can run in three primary modes:
1. FreeCAD Path Addon Gui
2. Standalone Gui, without FreeCAD
3. Console script (No gui and without FreeCAD)

In addition, there are expert and guided Gui modes.

## Status & Disclaimer
This calculator has many great features, but it is
**still** an *experimental* prototype and is be used at your own risk.
Machine tools are dangerous and this tools author(s) will not be responsible
for any damage or personal injury caused by incorrect machining parameters.

## Change History
### Initial release 2020-12-20 Version 0.1
* Select path tool controller, includes tool diameter, flutes and material
* Select workpiece material
* Set machining parameters
* User can override Chipload, Surface Speed or Spindle Speed
* Drilling vFeed
* Milling vFeed uses simple method that currently gives fast vertical feed rate.

### 2021-07-04 Version 0.2 
* example scripted use
* example of automatic CNC limits to outputs
* fix incorrect return value for rpm 

### 2021-07-12 Version 0.3
* Gui field reorder to match Tool, Feed, Speed and Outputs
* Write calculated outs back to selected ToolController in FreeCAD
* Drilling vFeed - temporarily removed due to layout changes made to meet forum suggestions

### 2022-01-??????? Version 0.4
* Users can now set Preferences, materials data, Tool definitions (standalone mode only).
    (materials data = Stock Material, hardness, SurfaceSpeed, Chipload, Kp, Kd, for milling & drilling and Hss/Cardbide tools)
* Material, Tool and preference data in csv files provides a LOT of user ability to tweak or load own data. 
    Also very flexible as column order can change and user can add additional colums (just ignored), so importing own Tools etc is v easy.
    But there is presently minimal validation, eg uniqueness of material & Tool names not enforced, or #Flutes <= 0, or missing values, etc
* Chipload look up has been enhanced to use curated data & wider range of tool diameters
* Axial chip Thinning (ATM scripted mode only, place holder fields are in "guided" mode)
* Some bug fixes and variable and python format refactoring in preparation for future enhancements
* Calculator can now run in three primary modes:
  1. FreeCAD Path Addon Gui
  2. Standalone Gui, without FreeCAD
  3. Console script (No gui and without FreeCAD)
* In addition to running as FreeCAD Addon, Standalone or scripted, there are "expert" and "guided" Gui modes.
* Care taken to ensure all four gui "ui" definition files {ie FreeCAD and Standalone versions of both "expert" "guided" guis} have minimal differences and same structure to ease maintenance.
* Care taken to ensure python code has minimal changes to support FreeCAD and Standalone versions
* Expert Gui mode appearance unchanged from v0.3
* Guided Gui mode features:
  - Inputs on left, outputs, including intermediate Lookup values on right.
  - Output overrides and CNC limit fields also on right hand side.
  - Background and highlights used to show similar elements.
  - Input and outputs loosely aligned with calculation order. Ideal would be arrows something like the "Required inputs for each calculation & calc order" image below, so user can clearly see which input affects which output.
  - Added Tips panel with instructions to guide user and more comphrensive tooltips* WIP Curated material data for Surface Speed and matching Chipload {needs work}
  - Wide range materials types from wax to plastic, wood and many metals
  - Default is condensed common material range
  - Users can edit/extend Surface Speed and Chipload data in a csv file
  - Hoping for community input to grow range and quality of data
  - Intend to open a FreeCAD forum post to discuss challenges and show some of the curve fits etc.
  - WIP Several data sets and some test data also supplied in test folder.
* Optional CNC limits
  - Act like user pre-set overrides that can be automaticaly applied, so horizontal FeedRate, Spindle Speed and Power can be auto-reduced to suit your mills ability
  - Scale relevant input to reduce corresponding output to set limit
  - Simple approach, needs improved algorithm for power limit.
  - Note: not yet implemented in "expert" mode.


[FreeCAD expert mode](/assets/images/FC_expert_mode.png)

[FreeCAD guided mode](/assets/images/FC_guided_mode.png)

[Script mode](/assets/images/Scripted_console.png)

[Required inputs for each calculation & calc order](/assets/images/Calculation_order_complete.png)


## Differences between FreeCAD, Standalone & Scripted console modes
* FreeCAD mode
  - Reads current FreeCAD document Path Jobs & gathers Tool controller attributes.
  - Allows updating calc output back into FC TC.

* Standalone modes
  - Some terminology changes, eg FreeCAD ToolController, becomes Tool
  - Tools & attributes read from csv file
  - TODO allow save calc outputs....

* Scripted console mode is only way that Chip Thinning & CNC limits, can currently be used. Placeholder fields have been added to Standalone gui, but remaining gui code not yet implemented.

## Requirements
* FreeCAD v0.19 or FreeCAD v0.20
* Python3  
* Qt5 (pyside2)

## Installation FreeCAD
1. Use `git clone` or download the `.zip` file of this repo directly in to your [FreeCAD `Mod/` directory](https://www.freecadweb.org/wiki/Installing_more_workbenches).  
2. Restart FreeCAD 
3. Open a FreeCAD design with at least one Path Job and ToolController
4. Start FreeCAD Feeds and Speeds Calculator from the Path - Addon menu.

## Installation Standalone or scripted use
1. Use `git clone` or download & unzip the repo `.zip` file into your selected directory
2. Install python3.x, pip3 & pyside2 (This should be easy, but  I had problems on some computers, so ask if you need help)
3. From directory in Step 1 run either:
   - python3 PathFeedsAndSpeedsGui.py
   - python3 scripted_TESTING.py

## Feedback & Contributing
If you have feedback or need to report bugs please participate on the related [FreeCAD Path Forum post](https://forum.freecadweb.org/viewtopic.php?f=15&t=59856). 

There are also plenty of ideas for added features, TODOs and FIXMEs in the code.

Pull requests and bug reports are welcome.
