"""
Plotting possibilities: 
(pyinstaller supported) --> matplotlib, pandas , 
                        seaborn, ggplot2

! pipenv run python RailwaySim_main.py

! pyuic5 -x RailwaySim_GUI.ui -o RailwaySim_GUI.py

! pipenv run pyinstaller --onefile RailwaySim_main.py

"""
import contextlib
from PyQt5.QtCore import QSettings, pyqtSlot  # Function wrapper
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw, uic
import os
from save_restore import guisave, guirestore

BASEDIR = os.path.dirname(__file__)


class MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mainEdits()

        #TODO selected from file dialog
        #TODO save button first to dialog, then to saved path
        self.my_settings = QtCore.QSettings(os.path.join(BASEDIR, "gui_data.ini"), QtCore.QSettings.IniFormat)

    def mainEdits(self):

        # ? Disable window resizing
        self.setFixedSize(self.size())

        # ? Icon paths fix
        self.actionSave.setIcon(QtGui.QIcon(os.path.join(BASEDIR, 'resources/images/save.png')))
        self.actionPreferences.setIcon(QtGui.QIcon(os.path.join(BASEDIR, 'resources/images/edit.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(BASEDIR, 'resources/images/new.png')))
        self.actionGitHub_Homepage.setIcon(QtGui.QIcon(os.path.join(BASEDIR, 'resources/images/github.png')))
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(BASEDIR, 'resources/images/open.png')))

        self.statusBar().showMessage(BASEDIR)

        # ? Test for pushbutton
        self.pushButton.clicked.connect(self.ShowMessage)

        # ? Toolbar button actions
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionExit.triggered.connect(self.close)

        # ? open and save triggers
        self.actionOpen.triggered.connect(self.read)
        self.actionSave_as.triggered.connect(self.write)
        self.actionSave.triggered.connect(self.write)

        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

        # self.actionSave.triggered.connect(self.save)

    def read(self):
        print("my_settings: ", self.my_settings)
        guirestore(self, self.my_settings)
        self.my_settings.isWritable()
        self.my_settings.fileName()
        self.my_settings.sync()

    def write(self):
        print("my_settings: ", self.my_settings)
        guisave(self, self.my_settings)
        self.my_settings.isWritable()
        self.my_settings.fileName()
        self.my_settings.sync()

    # Window exit button https://stackoverflow.com/questions/40622095/pyqt5-closeevent-method
    def closeEvent(self, event):
        close = qtw.QMessageBox.question(self, "Exit", "Exit application?", qtw.QMessageBox.Yes | qtw.QMessageBox.No)
        if close == qtw.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # TODO save and restore changes to widgets - see book
    """
    def openFileNameDialog(self):
        options = qtw.QFileDialog.Options()
        options |= qtw.QFileDialog.DontUseNativeDialog
        fileName, _ = qtw.QFileDialog.getOpenFileName(self, "Open file", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)

    def saveFileDialog(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(self, "Select the file to save to…", QtCore.QDir.homePath(), 'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)')
        if filename:
            try:
                with open(filename, 'w') as fh:
                    fh.write(self.textedit.toPlainText())
            except Exception as e:
                qtw.QMessageBox.critical(self, 'Error', f"Could not load file: {e}")
    """

    # ? capture data
    def ShowMessage(self):
        myNumber = self.doubleSpinBox_2.cleanText()
        qtw.QMessageBox.information(self, 'The number is:', myNumber)

    def GitHubLink(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/danicc097/RailwaySim'))

    # TODO animation when loading excel

    # TODO QMovie animation simulation
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