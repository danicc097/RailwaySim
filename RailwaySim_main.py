"""
Plotting possibilities: matplotlib, pandas, seaborn, ggplot2
"""

from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw

# ! Relative path fix
import os
path = os.path.dirname(os.path.abspath('RailwaySim_GUI.py'))


class MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mainEdits()

    def mainEdits(self):
        self.statusBar().showMessage('Welcome to RailwaySim')

        # ? Icon paths fix
        self.actionSave.setIcon(QtGui.QIcon(os.path.join(path, 'RailwaySim/resources/images/save.png')))
        self.actionPreferences.setIcon(QtGui.QIcon(os.path.join(path, 'RailwaySim/resources/images/edit.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(path, 'RailwaySim/resources/images/new.png')))
        self.actionGitHub_Homepage.setIcon(QtGui.QIcon(os.path.join(path, 'RailwaySim/resources/images/github.png')))
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(path, 'RailwaySim/resources/images/open.png')))

        self.pushButton.clicked.connect(self.ShowMessage)

    # ? capture data
    def ShowMessage(self):
        myNumber = self.doubleSpinBox_2.cleanText()
        qtw.QMessageBox.information(self, 'The number is:', myNumber)

    # TODO fix resources path


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Show our own modified class
    sys.exit(app.exec_())