# -*- coding: utf-8 -*-

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 Daniel Wood <s.d.wood.82@googlemail.com>            *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCADGui
from PySide import QtGui
import PathFeedsAndSpeedsGui
import os

__dir__ = os.path.dirname(__file__)
iconPath = os.path.join( __dir__, 'Icons' )

def getIcon(iconName):
     return os.path.join( iconPath , iconName)

def updateMenu(workbench):

    if workbench == 'PathWorkbench':
    
        print('Feeds and Speeds Addon loaded:', workbench)

        mw = FreeCADGui.getMainWindow()
        addonMenu = None

        # Find the main path menu
        pathMenu = mw.findChild(QtGui.QMenu, "&Path")

        for menu in pathMenu.actions():
            if menu.text() == "Path Addons":
                # create a new addon menu
                addonMenu = menu.menu()
                break

        if addonMenu is None:
            addonMenu = QtGui.QMenu("Path Addons")
            addonMenu.setObjectName("Path_Addons")

            # Find the dressup menu entry
            dressupMenu = mw.findChild(QtGui.QMenu, "Path Dressup")

            #addonMenu.setTitle("Path Addons")
            pathMenu.insertMenu(dressupMenu.menuAction(), addonMenu)

        # create an action for this addon
        action = QtGui.QAction(addonMenu)
        action.setText("Feeds and Speeds")
        action.setIcon(QtGui.QPixmap(getIcon('Path_FeedsAndSpeeds.svg')))
        action.setStatusTip("Check Feeds and Speeds")
        action.triggered.connect(PathFeedsAndSpeedsGui.Show)

        # append this addon to addon menu
        addonMenu.addAction(action)

FreeCADGui.getMainWindow().workbenchActivated.connect(updateMenu)
