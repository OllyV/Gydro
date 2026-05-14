

from math import dist

from qgis.core import (
    QgsWkbTypes,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsMapLayer,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)

# from qgis.gui import *
# from qgis.PyQt import QtCore, QtGui, uic
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QModelIndex, Qt, QVariant, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsMapTool, QgsRubberBand

from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDockWidget,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
)

from ..tools.GeometryCalculationHelper import GeometryCalculationHelper
from ..tools.lineSelector import LineSelector
from ..models.ProfileModel import ProfileModel

try:
    import matplotlib.pyplot as plt
    matplotlib_loaded = True
except ImportError:
    matplotlib_loaded = False

from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvas, FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

import numpy as np

# uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "solverdockwidget.ui"))
# FormClass = uic.loadUiType(uiFilePath)[0]



class SolverDockWidget(QDockWidget):

    TITLE = "Solver"
    TYPE = None

    closed = pyqtSignal()

    def __init__(self, iface1, plugincore, parent=None):
        self.plugincore = plugincore
        super().__init__(parent)

        ui_path = Path(__file__).resolve().parent / "solverdockwidget.ui"
        uic.loadUi(str(ui_path), self)

        self.iface = iface1
        self.canvas = self.iface.mapCanvas()
        self._set_up_CSectionSelector()
        self._set_up_ProfileSelector()

        self.CSectionsCount=1
        self.model = ProfileModel()

        self.location = Qt.DockWidgetArea.BottomDockWidgetArea
        minsize = self.minimumSize()
        maxsize = self.maximumSize()
        self.setMinimumSize(minsize)
        self.setMaximumSize(maxsize)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.label_helper.setText("Start by selecting cross sections." )
        self.showRubberBands = {}

        # Signals
        self.button_CSections_select.clicked.connect(self.selectCSection)
        self.button_Profile_select.clicked.connect(self.selectProfile)
        
        self.button_CSections_clear.clicked.connect(self.clearCSections)
        self.button_Profile_clear.clicked.connect(self.clearProfiles)
        self.spin_CSections_count.valueChanged.connect(self.updateCSectionsCount)
        self.comboBox_CSections_show.activated.connect(self.show_CSection_index)
        self.comboBox_Profile_select.activated.connect(self.show_Profile_index)

        self.button_Profile_calculate_by_deepest_points.clicked.connect(self.calculateProfileByDeepestPoints)

        layout = self.verticalLayout_CSections
        
        self._CSectionPlot = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self._CSectionPlot)
        layout.addWidget(NavigationToolbar(self._CSectionPlot, self))

        profileLayout = self.verticalLayout_Profile

        self._ProfilePlot = FigureCanvas(Figure(figsize=(5, 3)))
        profileLayout.addWidget(self._ProfilePlot)
        profileLayout.addWidget(NavigationToolbar(self._ProfilePlot, self))

        #self._CSectionPlot = self.plot_canvas
        #self._CSectionPlot = self._CSectionPlot.figure.subplots()

        # t = np.linspace(0, 10, 501)
        # self._static_ax.plot(t, np.tan(t), ".")


    # Cross section and profile selections
    
    def selectCSection(self):
        self.label_helper.setText("Select cross section and double click to end. \nCurrent cross section count " 
                                  + str(len(self.model.CSections)) 
                                  + "\nExpecting to add cross sections: " + str(self.CSectionsCount-len(self.model.CSections)))
        self.canvas.setMapTool(self.CSectionSelector)
    
    def selectProfile(self):
        self.label_helper.setText("Select Profile and double click to end.")
        self.canvas.setMapTool(self.ProfileSelector)

    def storeCSection(self, geom):
        num = len(self.model.CSections)
        self.addRubberBand(geom, 'CSection' + str(num), QColor(0, 200, 0, 255))
        self.comboBox_CSections_show.addItem("Cross section " + str(num))

        self.model.CSections.append(geom)
        
        if(len(self.model.CSections) < self.CSectionsCount):
            self.selectCSection()
        else:
            self.CSectionsCount=len(self.model.CSections)
            self.spin_CSections_count.setValue(self.CSectionsCount)
            
        self.label_helper.setText("Cross section added." + "\nCurrent cross section count " + str(len(self.model.CSections)))
        return
    
    def storeProfile(self, geom):
        if geom is None:
            self.label_helper.setText("Profile was not created.")
            return

        self.comboBox_Profile_select.addItem("Profile " + str(len(self.model.mainProfileLines)))
        self.addRubberBand(geom, 'Profile' + str(len(self.model.mainProfileLines)), QColor(0, 0, 250, 255))
        self.model.mainProfileLines.append(geom)
        self.label_helper.setText("Profile added." + "\nCurrent Profile count " + str(len(self.model.mainProfileLines)))
        return

    def clearCSections(self):
        self.model.CSections.clear()
        self.CSectionsCount = 0
        self.clearRubberBands('CSection')
        self.label_helper.setText("Cross section cleared.")
        self.spin_CSections_count.setValue(0)
        self.comboBox_CSections_show.clear()

    def clearProfiles(self):
        self.model.mainProfileLines.clear()
        self.clearRubberBands('Profile')
        self.label_helper.setText("Profiles cleared.")
        self.comboBox_Profile_select.clear()

    def updateCSectionsCount(self, value):
        if value > len(self.model.CSections):
            self.CSectionsCount=value
            self.label_helper.setText("Current cross section count " + str(len(self.model.CSections)) 
                                  + "\nExpecting to add cross sections: " + str(self.CSectionsCount - len(self.model.CSections)))
            return
        
    def calculateProfileByDeepestPoints(self):
        if len(self.model.CSections) < 2:
            self.label_helper.setText("Not enough cross sections to calculate profile. Please add more cross sections first.")
            return
        
        profilePoints = []
        for csection in self.model.CSections:
            deepestPoint = GeometryCalculationHelper.deepestPointOfGeometry(self.iface, csection)
            profilePoints.append(deepestPoint)

        self.storeProfile(QgsGeometry.fromPolylineXY(profilePoints))
        

    


    #RubberBand management

    def addRubberBand(self, geom, name, color):
        r = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        r.setColor(color)
        r.setWidth(2)
        r.setToGeometry(geom, None)
        self.showRubberBands[name] = r

    def clearRubberBands(self, pattern):
        for key in list(self.showRubberBands.keys()):
            if pattern in key:
                self.canvas.scene().removeItem(self.showRubberBands[key])
                self.showRubberBands.pop(key, None)


    #Set up settings

    def _set_up_CSectionSelector(self):
        def finished(geom):
            self.iface.mapCanvas().unsetMapTool(tool)
            self.storeCSection(geom)
        
        def cancelled():
            self.iface.mapCanvas().unsetMapTool(tool)
        red = QColor(200, 0, 0, 255)  # red
        
        tool = LineSelector(self.canvas, finished, cancelled, red)
        self.CSectionSelector = tool

    def _set_up_ProfileSelector(self):
        def finished(geom):
            self.iface.mapCanvas().unsetMapTool(tool)
            self.storeProfile(geom)
        
        def cancelled():
            self.iface.mapCanvas().unsetMapTool(tool)
        blue = QColor(0, 0, 250, 255)  # blue
        
        tool = LineSelector(self.canvas, finished, cancelled, blue)
        self.ProfileSelector = tool

    def closeEvent(self, event):
        self.clearRubberBands('Profile')
        self.clearRubberBands('CSection')
        self.plugincore.dockOpened = False


    # Graph showing

    def show_CSection_index(self, index):
        print("Index selected", index)
        self.showCSections(index)

    def show_Profile_index(self, index):
        print("Index selected", index)
        self.showProfile(index)

    def showCSections(self, number):
        if number > len(self.model.CSections):
            self.label_helper.setText("Invalid cross section number.")
            return
        
        geom = self.model.CSections[number]
        self.clearRubberBands('CSection_tmp')
        self.addRubberBand(geom, 'CSection_tmp', QColor(250, 0, 0, 255))

        depth = GeometryCalculationHelper.geometryToDepths(self.iface, geom)
        dz = np.arange(0, len(depth))

        pt = self._CSectionPlot.figure.subplots()
        pt.plot(dz, depth, color='red')
        self._CSectionPlot.draw_idle()

    def show_Profile_index(self, number):
        if number > len(self.model.mainProfileLines):
            self.label_helper.setText("Invalid profile number.")
            return
        
        geom = self.model.mainProfileLines[number]
        self.clearRubberBands('Profile_tmp')
        self.addRubberBand(geom, 'Profile_tmp', QColor(0, 250, 255, 255))

        depth = GeometryCalculationHelper.geometryToDepths(self.iface, geom)
        dz = np.arange(0, len(depth))

        pt = self._ProfilePlot.figure.subplots()
        pt.plot(dz, depth, color='blue')
        self._ProfilePlot.draw_idle()













