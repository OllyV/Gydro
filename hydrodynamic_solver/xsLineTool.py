

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import Qt, QObject, QEvent
from qgis.PyQt.QtGui import QCursor, QColor
from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog, QMenu

from qgis.core import (
    QgsProject, QgsWkbTypes, QgsFeature, QgsField,
    QgsVectorLayer, QgsGeometry, QgsPointXY, QgsCoordinateTransform
)
from qgis.gui import QgsMapTool, QgsRubberBand



class xsLineTool(QgsMapTool):
    def __init__(self, canvas, on_finished, on_cancelled):
        super().__init__(canvas)
        self.canvas = canvas
        self.on_finished = on_finished
        self.on_cancelled = on_cancelled
        self.points = []
        self.rb = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.rb.setColor(QColor(200, 0, 0, 255))  # red
        self.rb.setWidth(1)

    def activate(self):
        super().activate()
        self.canvas.setCursor(QCursor(Qt.CrossCursor))

    def deactivate(self):
        try:
            self.rb.reset(QgsWkbTypes.LineGeometry)
        except Exception:
            pass
        super().deactivate()

    def canvasPressEvent(self, e):
        if e.button() == Qt.RightButton:
            self._finish()
            return
        p = self.toMapCoordinates(e.pos())
        self.points.append(QgsPointXY(p))
        self.rb.addPoint(QgsPointXY(p), True)

    def canvasMoveEvent(self, e):
        if not self.points:
            return
        p = self.toMapCoordinates(e.pos())
        try:
            self.rb.movePoint(QgsPointXY(p))
        except Exception:
            pass

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._cancel()
            return
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._finish()
            return

    def _cancel(self):
        self.points = []
        try:
            self.rb.reset(QgsWkbTypes.LineGeometry)
        except Exception:
            pass
        if self.on_cancelled:
            self.on_cancelled()

    def _finish(self):
        if len(self.points) < 2:
            self._cancel()
            return
        geom = QgsGeometry.fromPolylineXY(self.points)
        if self.on_finished:
            self.on_finished(geom)