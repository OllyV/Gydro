
# -*- coding: utf-8 -*-
from pathlib import Path
import math
import re
import csv
from datetime import datetime

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt, QObject, QEvent
from qgis.PyQt.QtGui import QCursor, QColor
from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog, QMenu

from qgis.core import (
    QgsProject, QgsWkbTypes, QgsFeature, QgsField,
    QgsVectorLayer, QgsGeometry, QgsPointXY, QgsCoordinateTransform
)
from qgis.gui import QgsMapTool, QgsRubberBand



from pathlib import Path
import math
import re
import csv
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .xsLineTool import xsLineTool


class SolverDialog(QtWidgets.QDialog):
    
    def _set_xs_geometry(self,geom):
        
        #self.iface.mapCanvas().unsetMapTool(tool)

        geo = geom
        print(geom)
        pl = geom.asPolyline()

        if not pl:
            mpl = geom.asMultiPolyline()
            if mpl and mpl[0]:
                pl = mpl[0]
        
        for i, pt in enumerate(pl):
            self._rb_xs.addPoint(QgsPointXY(pt), i == (len(pl)-1))
        
        step = 1.0
        length = geom.length()
    
        n = max(2, int(math.floor(length / step)) + 1)
        provider = self.iface.activeLayer().dataProvider()
        print(provider)
    
        if not length or length <= 0.01:
            print("XS length too small.")
            return
    
        for i in range(n):
            d = min(length, i * step)
            print(d)
            pt = geom.interpolate(d).asPoint()
            print(pt)
            val = provider.sample(QgsPointXY(pt), 1)[0]
            print(val)
            self.samples_full.append({"x": float(d), "z": float(val)})
        
        bed_datum = min(s["z"] for s in self.samples_full)

        print(self.samples_full)
        fig = plt.figure(figsize=(5, 3), dpi=100)
        plt.plot([0, 1], [2, 3])
        plt.close(fig)
        
        def _adaptive_decimate(xs, zs):
            n = len(xs)
            if n <= 1000:
                return xs, zs
            step = max(1, n // 1500)
            return xs[::step], zs[::step]
        
        ax = fig.add_subplot(111)
        ax.set_xlabel("Chainage (m)")
        ax.set_ylabel("Elevation (m)")
        
        xs = [s["x"] for s in self.samples_full]
        zs = [s["z"] for s in self.samples_full]
        dxs, dzs = _adaptive_decimate(xs, zs)
        xmin = min(xs)
        xmax = max(xs)
        ax.plot(dxs, dzs, linewidth=1.5, color="black", label="Bed")
        print(ax)
        print(fig)
        canvas = FigureCanvas(fig)
        canvas.show()
    
    def on_draw_xs(self):
        canvas = self.iface.mapCanvas()

        def finished(geom):
            self.iface.mapCanvas().unsetMapTool(tool)
            self._set_xs_geometry(geom)

        def cancelled():
            self.iface.mapCanvas().unsetMapTool(tool)

        tool = xsLineTool(canvas, finished, cancelled)
        canvas.setMapTool(tool)

    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        ui_path = Path(__file__).resolve().parent / "hydrodynamic_solver.ui"
        uic.loadUi(str(ui_path), self)
        
        canvas = iface.mapCanvas()
        canvas.show()

        geo = QgsGeometry()
        self._rb_xs = QgsRubberBand(iface.mapCanvas(), QgsWkbTypes.LineGeometry)
        self._rb_xs.setColor(QColor(200, 0, 0, 255))  # red
        self._rb_xs.setWidth(1)
        self._rb_xs.show()
        self.samples_full = []

        self.selectSliceButton.clicked.connect(self.on_draw_xs)
