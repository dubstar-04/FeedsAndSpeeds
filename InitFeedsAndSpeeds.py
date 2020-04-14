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
    print('Workbench loaded:', workbench)

    if workbench == 'PathWorkbench':
        print('load the helper menu')
        mw = FreeCADGui.getMainWindow()
        menu = mw.findChildren(QtGui.QMenu, "Supplemental Commands")[0]
        action = QtGui.QAction(menu)
        action.setText("Feeds and Speeds")
        action.setIcon(QtGui.QPixmap(getIcon('Path_FeedsAndSpeeds.svg')))
        #action.setObjectName("Path")
        action.setStatusTip("Check Feeds and Speeds")
        action.triggered.connect(PathFeedsAndSpeedsGui.Show)
        menu.addAction(action)

FreeCADGui.getMainWindow().workbenchActivated.connect(updateMenu)