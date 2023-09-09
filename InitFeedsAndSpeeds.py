# -*- coding: utf-8 -*-

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020-2023 Daniel Wood <s.d.wood.82@googlemail.com>      *
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

import os

import FreeCADGui
from PySide import QtGui
import PathFeedsAndSpeedsGui
import PathAddonCommon


def getIcon(iconName):
    __dir__ = os.path.dirname(__file__)
    iconPath = os.path.join(__dir__, 'Icons')
    return os.path.join(iconPath, iconName)


def getAction(mw, name):
    """Get a QAction to show the feeds and speeds icon and launch the form"""
    FeedsAndSpeedsAction = QtGui.QAction(mw)
    FeedsAndSpeedsAction.setObjectName(name)
    FeedsAndSpeedsAction.setIconText("Feeds and Speeds")
    FeedsAndSpeedsAction.setStatusTip("Check Feeds and Speeds")
    FeedsAndSpeedsAction.setIcon(QtGui.QPixmap(getIcon('Path_FeedsAndSpeeds.svg')))
    FeedsAndSpeedsAction.triggered.connect(PathFeedsAndSpeedsGui.Show)
    return FeedsAndSpeedsAction


def updateMenu(workbench):
    """Load the feeds and speeds menu and toolbar"""
    if workbench == 'PathWorkbench':
        print('Feeds and Speeds Addon loaded:', workbench)

        mw = FreeCADGui.getMainWindow()
        PathAddonCommon.loadToolBar("Feeds and Speeds", [getAction(mw, "FeedsandSpeedsToolbarAction")])

        pathAddonMenu = PathAddonCommon.loadPathAddonMenu()
        FeedsAndSpeedsAction = mw.findChild(QtGui.QAction, "FeedsandSpeedsMenuAction")

        if not FeedsAndSpeedsAction:
            # create addon action
            pathAddonMenu.addAction(getAction(mw, "FeedsandSpeedsMenuAction"))


FreeCADGui.getMainWindow().workbenchActivated.connect(updateMenu)
