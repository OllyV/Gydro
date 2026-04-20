
import os

from qgis.core import (
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

    def __init__(self, iface1, lineselector, parent=None):
        
        super().__init__(parent)
        ui_path = Path(__file__).resolve().parent / "solverdockwidget.ui"
        uic.loadUi(str(ui_path), self)

        # QDockWidget.__init__(self, parent)

        # self.setupUi(self)

        self.lineselector = lineselector
        self.iface = iface1

        self.location = Qt.DockWidgetArea.BottomDockWidgetArea
        minsize = self.minimumSize()
        maxsize = self.maximumSize()
        self.setMinimumSize(minsize)
        self.setMaximumSize(maxsize)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.label_helper.setText("Start by selecting profiles." )

        # Signals
        self.button_profiles_select.clicked.connect(self.addProfiles)



    def addProfiles(self):
        return


    





