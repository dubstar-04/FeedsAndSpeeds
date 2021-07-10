# Feed and Speed Calculator
# Provides a basic feeds and speeds calculator for use with FreeCAD Path

import FreeCAD, FreeCADGui
import os

import PathFeedsAndSpeeds

dir = os.path.dirname(__file__)
ui_name = "PathFeedsAndSpeedsGui.ui"
path_to_ui = dir + "/" + ui_name


class FeedSpeedPanel():
    def __init__(self):
        # Build GUI
        self.form = FreeCADGui.PySideUic.loadUi(path_to_ui)

        # Set Defaults
        self.toolDia = 6

        # Init
        self.calculation = PathFeedsAndSpeeds.FSCalculation()
        self.setup_ui()
        self.calculate()

        # connect
        self.form.material_CB.currentIndexChanged.connect(self.set_surface_speed)
        self.form.hss_RB.toggled.connect(self.calculate)
        self.form.cbd_RB.toggled.connect(self.calculate)
        self.form.toolDia_LE.textChanged.connect(self.calculate)
        self.form.flutes_SB.valueChanged.connect(self.calculate)
        self.form.FPT_SB.valueChanged.connect(self.calculate)
        self.form.WOC_SP.textChanged.connect(self.calculate)
        self.form.DOC_SP.textChanged.connect(self.calculate)
        self.form.rpm_LE.textChanged.connect(self.calculate)
        self.form.toolController_CB.currentIndexChanged.connect(self.load_tool_properties)
        self.form.update_PB.clicked.connect(self.update_tool_controller)
        self.form.close_PB.clicked.connect(self.quit)

    def setup_ui(self):
        # load materials
        # materials = PathFeedsAndSpeeds.load_materials()
        for material in (d['material'] for d in PathFeedsAndSpeeds.load_materials()):
            self.form.material_CB.addItem(material)

        # load widget data
        self.set_tool_properties(self.toolDia, 2, self.toolDia * 0.01, "HSS")

        self.load_tools()
        self.load_tool_properties()
        self.set_tool_material()
        self.set_surface_speed()

    def set_tool_properties(self, dia, flutes, chipload, material):
        self.form.toolDia_LE.setText(str(dia))
        self.form.flutes_SB.setValue(flutes)
        self.form.FPT_SB.setValue(chipload)

        self.form.WOC_SP.setText(str(round(dia * 0.2, 2)))
        self.form.DOC_SP.setText(str(dia))

        if material == "HSS":
            self.form.hss_RB.setChecked(True)
        elif material == "Carbide":
            self.form.cbd_RB.setChecked(True)

    def set_surface_speed(self):
        material = self.form.material_CB.currentText()

        self.calculation.set_material(material)

        ss = self.calculation.get_surface_speed()
        print("Surface Speed:", ss, material)

        self.form.ss_LE.setText(str(ss))
        self.calculate

    def set_tool_material(self):
        self.calculation.ss_by_material = "ss_hss" if self.form.hss_RB.isChecked() else "ss_cbd"

    def load_tools(self):
        jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
        # self.form.toolController_CB.addItem('None')
        for job in jobs:
            for idx, tc in enumerate(job.Tools.Group):
                self.form.toolController_CB.addItem(tc.Label)

    def load_tool_properties(self):
        tc = self.get_tool_controller()

        if tc:
            tool = tc.Tool
            dia = tool.Diameter
            flutes = tool.Flutes
            material = tool.Material
            chipload = tool.Chipload
            self.set_tool_properties(dia, flutes, chipload, material)
            print("tool props:", dia, flutes, material, chipload)

    def get_tool_controller(self):
        jobs = FreeCAD.ActiveDocument.findObjects("Path::FeaturePython", "Job.*")
        tcStr = self.form.toolController_CB.currentText()
        for job in jobs:
            for tc in job.Tools.Group:
                if tc.Label == tcStr:
                    return tc

        return None

    def update_tool_controller(self):
        tc = self.get_tool_controller()

        if tc:
            rpm = self.form.rpm_result.text()
            feed = self.form.feed_result.text()
            # TODO: Add a confirmation dialog
            tc.HorizFeed = feed
            tc.SpindleSpeed = float(rpm)

    def calculate(self):

        if self.calculation.material is None:
            return

        tool = PathFeedsAndSpeeds.Tool()

        self.calculation.rpm_overide = self.form.rpm_LE.text()

        if not self.form.rpm_LE.text() == "":
            self.form.rpm_result.setEnabled(False)
        else:
            self.form.rpm_result.setEnabled(True)

        # if self.tabWidget.currentIndex() == 0:
            # calculate for milling
        tool.toolDia = FreeCAD.Units.Quantity(self.form.toolDia_LE.text())
        tool.flutes = self.form.flutes_SB.value()
        self.calculation.feedPerTooth = float(self.form.FPT_SB.value())
        self.calculation.WOC = FreeCAD.Units.Quantity(self.form.WOC_SP.text())
        self.calculation.DOC = FreeCAD.Units.Quantity(self.form.DOC_SP.text())
        self.calculation.toolWear = 1.1  # Tool Wear pg: 1048
        self.set_tool_material()
        self.calculation.opType = 'Milling'

        """
        else:
            # calculate for drilling
            tool.toolDia = float(self.drillDia_LE.text())
            calculation.feedPerTooth = float(self.drillFPT_SB.value())
            calculation.toolWear = 1.3 ## Tool Wear pg: 1048
            calculation.ss_by_material = "ss_drill_hss" if self.hss_RB.isChecked() else "ss_drill_cbd"
            calculation.opType = 'Drilling'
            print('tooldia', tool.toolDia)
            if tool.toolDia:
                notes = 'Note: Peck drilling should be used when hole depth > {0}'
                self.drilling_notes.setText(notes.format(tool.toolDia * 4))
            else:
                self.drilling_notes.setText('')
        """

        if not self.calculation.feedPerTooth:
            return

        rpm, feed, Hp = self.calculation.calculate(tool)
        watts = Hp * 745.69

        self.form.rpm_result.setText(str(rpm))
        self.form.feed_result.setText(str(feed) + " mm/min")
        self.form.hp_result.setText(str(round(Hp, 2)) + " hp / " + str(round(watts, 2)) + " watts")

    def show(self):
        self.form.show()
        self.form.exec_()

    def reject(self):
        FreeCAD.Console.PrintMessage("Reject Signal")
        self.quit()

    def accept(self):
        self.quit()

    def quit(self):
        self.form.close()

    def reset(self):
        pass


def Show():
    panel = FeedSpeedPanel()
    panel.show()
