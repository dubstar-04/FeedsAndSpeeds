# -*- coding: utf-8 -*-

# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Daniel Wood <s.d.wood.82@googlemail.com>            *
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


def loadPathAddonMenu():
    mw = FreeCADGui.getMainWindow()
    mb = mw.menuBar()

    # Find the path addon menu
    pathAddonAction = mw.findChild(QtGui.QAction, "PathAddons")

    if pathAddonAction:
        pathAddonMenu = pathAddonAction.menu()
    else:
        pathAddonAction = QtGui.QAction(mw)
        pathAddonAction.setObjectName("PathAddons")
        pathAddonAction.setIconText("Path Addons")

        pathAddonMenu = QtGui.QMenu("Path Addon Menu")
        pathAddonMenu.setObjectName("PathAddonMenu")

        pathAddonAction.setMenu(pathAddonMenu)

    menuLoaded = False
    for action in mb.actions():
        if action.objectName() == "PathAddons":
            menuLoaded = True
            break

    if not menuLoaded:
        # add addon to the menu bar
        mb.addAction(pathAddonAction)

    return pathAddonMenu


def loadToolBar(name, actions):
    """Load a toolbar in the path workbench"""
    mw = FreeCADGui.getMainWindow()
    tb = QtGui.QToolBar(name)
    tb.setObjectName(name + "_ToolBar")

    for action in actions:
        tbb = QtGui.QToolButton(tb)
        # tbb.setObjectName("ToolButton")
        tbb.setDefaultAction(action)
        tb.addWidget(tbb)

    mw.addToolBar(tb)
