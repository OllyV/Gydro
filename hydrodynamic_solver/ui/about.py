
# import os
# import platform

# from qgis.PyQt import uic
# from qgis.PyQt.QtCore import *
# from qgis.PyQt.QtGui import *
# from qgis.PyQt.QtWidgets import QDialog

# uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "about.ui"))
# FormClass = uic.loadUiType(uiFilePath)[0]

# class DialogAbout(QDialog, FormClass):
#     def __init__(self, parent=None):
#         QDialog.__init__(self, parent)
#         self.setupUi(self)

#         fp = os.path.join(
#             os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "metadata.txt"
#         )

#         aboutTxt = QSettings(fp, QSettings.IniFormat)
#         verno = aboutTxt.value("version")
#         name = aboutTxt.value("name")
#         description = aboutTxt.value("description")

#         self.title.setText(name)
#         self.description.setText(description + " - " + verno)
