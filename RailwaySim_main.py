"""
Plotting possibilities: 
(pyinstaller supported) --> matplotlib, pandas , 
                        seaborn, ggplot2

! pipenv run python RailwaySim_main.py

! pyuic5 -x RailwaySim_GUI.ui -o RailwaySim_GUI.py 
! pyuic5 -x RailwaySim_GUI_pref.ui -o RailwaySim_GUI_pref.py
! pipenv run pyinstaller --onefile RailwaySim_main.py

"""
import PyQt5
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QPalette
import PyQt5.QtPrintSupport as qtps
from PyQt5.QtWidgets import QDialog, QWidget
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw, uic
import os
from save_restore import guisave, guirestore
from RailwaySim_GUI_pref import Ui_Form

BASEDIR = os.path.dirname(__file__)


class MainWindow(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.config_is_set = 0  # Call tracker
        self.statusBar().showMessage(BASEDIR)
        self.mainEdits()
        self.iconFixes()

    # TODO dark mode replace "_dark.png"
    def iconFixes(self, styleSheet=False):
        global darkPath
        if not styleSheet:
            darkPath = 'resources/images/'
        if styleSheet:
            darkPath = 'resources/images_dark/'
        self.actionSave.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'save.png')))
        print(os.path.join(BASEDIR, darkPath, 'save.png'))
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'open.png')))
        self.actionAbout.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'about.png')))
        self.actionEdit.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'settings.png')))
        self.actionExit.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'exit.png')))
        self.actionPrintToPDF.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'print.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'new.png')))
        self.actionGitHub_Homepage.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'github.png'))
        )
        self.E_TECurveEditButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'edit_csv.png'))
        )
        self.E_TECurveLoadButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'import_csv.png'))
        )
        self.E_BECurveEditButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'edit_csv.png'))
        )
        self.E_BECurveLoadButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'import_csv.png'))
        )
        self.D_TECurveEditButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'edit_csv.png'))
        )
        self.D_TECurveLoadButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'import_csv.png'))
        )
        self.D_BECurveEditButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'edit_csv.png'))
        )
        self.D_BECurveLoadButton.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'import_csv.png'))
        )

    def mainEdits(self):
        # ? Disable window resizing
        self.setFixedSize(self.size())

        # ? Test for pushbutton
        self.pushButton.clicked.connect(self.ShowMessage)

        # ? Toolbar button actions
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionAbout.triggered.connect(self.AboutInfo)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit.triggered.connect(self.preferences_window)

        # ? open and save triggers
        self.actionNew_Window.triggered.connect(self.newFile)
        self.actionOpen.triggered.connect(self.readFile)
        self.actionSave.triggered.connect(self.writeFile)
        self.actionSave_as.triggered.connect(self.writeNewFile)

        # TODO PDF - See invoice_maker
        # self.printer = qtps.QPrinter()
        # self.printer.setOrientation(qtps.QPrinter.Portrait)
        # self.printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        #self.actionPrintToPDF.triggered.connect(self.export_pdf)

        # TODO csv

        # ? window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

    def newFile(self):  # ? New empty instance
        clear = qtw.QMessageBox.warning(
            self, "Clear contents", "Clear all fields? Any changes will be lost.",
            qtw.QMessageBox.Yes | qtw.QMessageBox.No
        )
        if clear == qtw.QMessageBox.Yes:
            self.win = NewWindow()
            self.win.show()
            self.hide()

    def writeNewFile(self):  # ? Save as
        self.config_is_set += 1
        self.filename, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Select where to save the configuration file…",
            BASEDIR,
            'Configuration Files (*.ini)',
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        self.statusBar().showMessage(self.filename)
        if self.filename.lower().endswith('.ini'):
            try:
                self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
                guisave(self, self.my_settings)
                self.my_settings.sync()
                self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
            except Exception as e:
                qtw.QMessageBox.critical(self, f"Could not save settings: {e}")

    def readFile(self):  # ? Open
        self.config_is_set += 1
        self.filename, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select a configuration file to load…",
            BASEDIR,
            'Configuration Files (*.ini)',
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        if self.filename == "":
            qtw.QMessageBox.critical(
                self, "Operation aborted", "Empty filename or none selected. \n Please try again.",
                qtw.QMessageBox.Ok
            )
            self.statusBar().showMessage("Select a valid configuration file")
        else:
            if self.filename.lower().endswith('.ini'):
                try:
                    self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
                    guirestore(self, self.my_settings)
                    self.my_settings.sync()
                    self.statusBar().showMessage("Changes being saved to: {}".format(self.filename))
                    self.setWindowTitle(os.path.basename(self.filename))
                except Exception as e:
                    qtw.QMessageBox.critical(self, f"Could not open settings: {e}")
            else:
                qtw.QMessageBox.critical(
                    self, "Invalid file type", "Please select a .ini file.", qtw.QMessageBox.Ok
                )

    def writeFile(self):  # ? Save
        if self.config_is_set:
            if self.filename != "":
                self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
                self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
                guisave(self, self.my_settings)
                self.my_settings.sync()
            else:
                self.writeNewFile()
        else:
            self.writeNewFile()

    # ? capture data
    def ShowMessage(self):
        myNumber = self.doubleSpinBox_2.cleanText()
        qtw.QMessageBox.information(self, 'The number is:', myNumber)

    def AboutInfo(self):
        infoScreen = qtw.QMessageBox()
        infoScreen.setWindowTitle('Legal Information')
        infoScreen.setText('RailwaySim is licenced under the GNU GPL.')
        infoScreen.setInformativeText("The complete license is available below.")
        try:
            infoScreen.setDetailedText(
                open(os.path.join(BASEDIR, "LICENSE"), "r", encoding="utf-8").read()
            )
        except:
            infoScreen.setDetailedText("http://www.gnu.org/licenses/gpl-3.0.en.html")
        infoScreen.setWindowModality(QtCore.Qt.WindowModal)
        infoScreen.resize(250, 150)
        infoScreen.exec()

    def GitHubLink(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/danicc097/RailwaySim'))

    # TODO _print_document()
    # def export_pdf(self):
    #     filename, _ = qtw.QFileDialog.getSaveFileName(
    #         self, "Save to PDF", QtCore.QDir.homePath(), "PDF Files (*.pdf)"
    #     )
    #     if filename:
    #         self.printer.setOutputFileName(filename)
    #         self.printer.setOutputFormat(qtps.QPrinter.PdfFormat)
    #         self._print_document()

    def closeEvent(self, event):
        """Accept or Ignore event action"""
        close = qtw.QMessageBox.question(
            self, "Exit", "Exit application?", qtw.QMessageBox.Yes | qtw.QMessageBox.No
        )
        if close == qtw.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def preferences_window(self):
        self.pref_screen = Preferences()
        # ApplicationModal to block input in all windows
        self.pref_screen.setWindowModality(QtCore.Qt.ApplicationModal)
        self.pref_screen.setFocus(True)
        self.pref_screen.show()


class Preferences(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cb_dark.stateChanged.connect(self.cb_dark_check)
        self.cb_watermark.stateChanged.connect(self.cb_watermark_check)

    def cb_dark_check(self):
        try:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet())
            window.iconFixes(styleSheet=True)

            if not self.cb_dark.isChecked():
                app.setStyleSheet("")
                window.iconFixes()
        except:
            qtw.QMessageBox.critical(self, "Error", "Could not set all stylesheet settings.")

    def cb_watermark_check(self):
        if self.cb_watermark.isChecked():
            global chart_watermark
            chart_watermark = self.watermark.text()
            chart_watermark_global()


def chart_watermark_global():
    print(chart_watermark)
    # TODO matplotlib

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


# * There is no restriction on the number of QMainWindow instances
# ! There is a limitation of one QApplication per process
class NewWindow(MainWindow):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    import sys
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Show our own modified class

    # ? Exit with Ctrl + C
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec_())