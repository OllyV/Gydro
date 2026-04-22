
import os
import re

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

# plugin import
from ..tools.lineSelector import LineSelector
from ..models.flowModel import FlowModel, ProfileModel

try:
    import matplotlib  # noqa:F401
    from matplotlib import *  # noqa:F403,F401

    matplotlib_loaded = True
except ImportError:
    matplotlib_loaded = False

from pathlib import Path

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
        self._set_up_profileSelector()
        self._set_up_flowSelector()

        self.profilesCount=1
        self.model = FlowModel()

        self.location = Qt.DockWidgetArea.BottomDockWidgetArea
        minsize = self.minimumSize()
        maxsize = self.maximumSize()
        self.setMinimumSize(minsize)
        self.setMaximumSize(maxsize)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.label_helper.setText("Start by selecting profiles." )
        self.showRubberBands = {}

        # Signals
        self.button_profiles_select.clicked.connect(self.selectProfile)
        self.button_flow_select.clicked.connect(self.selectFlow)
        
        self.button_profiles_clear.clicked.connect(self.clearProfiles)
        self.button_flow_clear.clicked.connect(self.clearFlows)
        self.spin_profiles_count.valueChanged.connect(self.updateProfilesCount)

    
    def selectProfile(self):
        self.label_helper.setText("Select profile and double click to end. \nCurrent profile count " 
                                  + str(len(self.model.profiles)) 
                                  + "\nExpecting to add profiles: " + str(self.profilesCount-len(self.model.profiles)))
        self.canvas.setMapTool(self.profileSelector)
    
    def selectFlow(self):
        self.label_helper.setText("Select flow and double click to end.")
        self.canvas.setMapTool(self.flowSelector)

    def storeProfile(self, geom):
        self.addRubberBand(geom, 'profile' + str(len(self.model.profiles)), QColor(0, 200, 0, 255))
        self.model.profiles.append(geom)
        
        if(len(self.model.profiles) < self.profilesCount):
            self.selectProfile()
        else:
            self.profilesCount=len(self.model.profiles)
            self.spin_profiles_count.setValue(self.profilesCount)
            
        self.label_helper.setText("Profile added." + "\nCurrent profile count " + str(len(self.model.profiles)))
        return
    
    def storeFlow(self, geom):
        self.addRubberBand(geom, 'flow' + str(len(self.model.mainFlowLines)), QColor(0, 0, 250, 255))
        self.model.mainFlowLines.append(geom)
        self.label_helper.setText("Flow added." + "\nCurrent flow count " + str(len(self.model.mainFlowLines)))
        return
    
    def clearProfiles(self):
        self.model.profiles.clear()
        self.profilesCount = 0
        self.clearRubberBands('profile')
        self.label_helper.setText("Profiles cleared.")
        self.spin_profiles_count.setValue(0)

    def clearFlows(self):
        self.model.mainFlowLines.clear()
        self.clearRubberBands('flow')
        self.label_helper.setText("Flows cleared.")

    def updateProfilesCount(self, value):
        if value > len(self.model.profiles):
            self.profilesCount=value
            self.label_helper.setText("Current profile count " + str(len(self.model.profiles)) 
                                  + "\nExpecting to add profiles: " + str(self.profilesCount - len(self.model.profiles)))
            return
        
        



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

    def _set_up_profileSelector(self):
        def finished(geom):
            self.iface.mapCanvas().unsetMapTool(tool)
            self.storeProfile(geom)
        
        def cancelled():
            self.iface.mapCanvas().unsetMapTool(tool)
        red = QColor(200, 0, 0, 255)  # red
        
        tool = LineSelector(self.canvas, finished, cancelled, red)
        self.profileSelector = tool

    def _set_up_flowSelector(self):
        def finished(geom):
            self.iface.mapCanvas().unsetMapTool(tool)
            self.storeFlow(geom)
        
        def cancelled():
            self.iface.mapCanvas().unsetMapTool(tool)
        blue = QColor(0, 0, 250, 255)  # blue
        
        tool = LineSelector(self.canvas, finished, cancelled, blue)
        self.flowSelector = tool

    def closeEvent(self, event):
        self.clearRubberBands('flow')
        self.clearRubberBands('profile')
        self.plugincore.dockOpened = False

