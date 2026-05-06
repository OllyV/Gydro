
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QWidget
from qgis.PyQt.QtGui import QColor

from .tools.lineSelector import LineSelector
from .ui.solverDockWidget import SolverDockWidget

# plugin import
#from .models.flowModel import FlowModel

class SolverCore(QWidget):

    def __init__(self, iface, plugincore, parent=None):
        QWidget.__init__(self, parent)
        self.plugincore = plugincore
        self.iface = iface
        self.profilesCount=0

        self.dockwidget = SolverDockWidget(self.iface, self)
        # self._set_up_profileSelector()
        # self._set_up_flowSelector()
        self._setup_profile_count_change()
        
        #self.model = FlowModel()


    # def _set_up_profileSelector(self):
    #     canvas = self.iface.mapCanvas()

    #     def finished(geom):
    #         self.iface.mapCanvas().unsetMapTool(tool)
    #         self.storeProfile(geom)
        
    #     def cancelled():
    #         self.iface.mapCanvas().unsetMapTool(tool)
    #     red = QColor(200, 0, 0, 255)  # red
        
    #     tool = LineSelector(canvas, finished, cancelled, red)
    #     self.dockwidget.canvas = canvas
    #     self.dockwidget.profileSelector = tool
    
    
    # def _set_up_flowSelector(self):
    #     canvas = self.iface.mapCanvas()

    #     def finished(geom):
    #         self.iface.mapCanvas().unsetMapTool(tool)
    #         self.storeFlow(geom)
        
    #     def cancelled():
    #         self.iface.mapCanvas().unsetMapTool(tool)
    #     blue = QColor(0, 0, 200, 255)  # blue
        
    #     tool = LineSelector(canvas, finished, cancelled, blue)
    #     self.dockwidget.flowSelector = tool

    # def storeProfile(self, geom):
    #     self.model.profiles.append(geom)

    #     if(len(self.model.profiles) < self.profilesCount):
    #         self.dockwidget.addProfile()

    #     return
    
    # def storeFlow(self, geom):
    #     self.model.mainFlowLines.append(geom)
    #     return
    
    # def _setup_profile_count_change(self):
    #     def count_change(value):
    #         self.profilesCount=value

    #     self.dockwidget.onProfilesCountChange = count_change





