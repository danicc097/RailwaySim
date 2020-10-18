"""
Plotting possibilities: 
(pyinstaller supported) --> matplotlib, pandas , 
                        seaborn, ggplot2


! pipenv run python RailwaySim_main.py

"""

from PyQt5.QtCore import pyqtSlot
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw, uic, QtQml
import os


class MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mainEdits()

    def mainEdits(self):

        # ? Icon paths fix
        path = os.path.dirname(os.path.abspath('RailwaySim_GUI.py'))
        self.actionSave.setIcon(QtGui.QIcon(os.path.join(path, 'resources/images/save.png')))
        self.actionPreferences.setIcon(QtGui.QIcon(os.path.join(path, 'resources/images/edit.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(path, 'resources/images/new.png')))
        self.actionGitHub_Homepage.setIcon(QtGui.QIcon(os.path.join(path, 'resources/images/github.png')))
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(path, 'resources/images/open.png')))

        self.statusBar().showMessage(path)

        # ? Test for pushbutton
        self.pushButton.clicked.connect(self.ShowMessage)

        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)

    # ? capture data
    def ShowMessage(self):
        myNumber = self.doubleSpinBox_2.cleanText()
        qtw.QMessageBox.information(self, 'The number is:', myNumber)

    def GitHubLink(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/danicc097/RailwaySim'))

    # TODO animation when loading excel

    # TODO QMovie animation
    # self.movie = QMovie("{filename}.gif")
    # self.movie.frameChanged.connect(self.repaint)
    # self.movie.start()

    # def paintEvent(self, event):
    #     currentFrame = self.movie.currentPixmap()
    #     frameRect = currentFrame.rect()
    #     frameRect.moveCenter(self.rect().center())
    #     if frameRect.intersects(event.rect()):
    #         painter = QPainter(self)
    #         painter.drawPixmap(frameRect.left(), frameRect.top(), currentFrame)

    # TODO file managing


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Show our own modified class

    # ! Exit with Ctrl + C
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec_())