

from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QWidget

from .tools.lineSelector import LineSelector
from .ui.solverDockWidget import SolverDockWidget

# plugin import
from .models.flowModel import FlowModel


class SolverCore(QWidget):
    def __init__(self, iface, plugincore, parent=None):
        QWidget.__init__(self, parent)
        self.plugincore = plugincore
        self.iface = iface

        self.dockwidget = SolverDockWidget(self.iface, self)
        
        self.model = FlowModel()