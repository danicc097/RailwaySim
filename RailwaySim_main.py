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
from PyQt5.QtWidgets import QDialog, QWidget, QSizePolicy
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw, uic
import os
from save_restore import guisave, guirestore
from RailwaySim_GUI_pref import Ui_Form
import integrated_csv_editor

BASEDIR = os.path.dirname(__file__)

# TODO interpolate widget size upon resize

# TODO resize app based on resolution

# TODO center new windows based on mainWindow current location

# TODO new .ini file for theme preference on startup


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
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'open.png')))
        self.actionAbout.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'about.png')))
        self.actionEdit.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'settings.png')))
        self.actionExit.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'exit.png')))
        self.actionPrintToPDF.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'print.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'new.png')))
        self.actionGitHub_Homepage.setIcon(
            QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'github.png'))
        )
        icon_edit = QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'edit_csv.png'))
        icon_import = QtGui.QIcon(os.path.join(BASEDIR, darkPath, 'import_csv.png'))
        self.E_TECurveEditButton.setIcon(icon_edit)
        self.E_TECurveLoadButton.setIcon(icon_import)
        self.E_BECurveEditButton.setIcon(icon_edit)
        self.E_BECurveLoadButton.setIcon(icon_import)
        self.D_TECurveEditButton.setIcon(icon_edit)
        self.D_TECurveLoadButton.setIcon(icon_import)
        self.D_BECurveEditButton.setIcon(icon_edit)
        self.D_BECurveLoadButton.setIcon(icon_import)

    def mainEdits(self):
        # ? Disable window resizing
        #self.setFixedSize(self.size())

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

        # ? CSV import buttons - anon to prevent autostart
        self.E_TECurveLoadButton.clicked.connect(
            lambda: self.path_extractor(self.E_TECurveLoadFilename)
        )
        self.E_BECurveLoadButton.clicked.connect(
            lambda: self.path_extractor(self.E_BECurveLoadFilename)
        )
        self.D_TECurveLoadButton.clicked.connect(
            lambda: self.path_extractor(self.D_TECurveLoadFilename)
        )
        self.D_BECurveLoadButton.clicked.connect(
            lambda: self.path_extractor(self.D_BECurveLoadFilename)
        )

        # ? CSV edit buttons
        self.E_TECurveEditButton.clicked.connect(
            lambda: self.csv_editor(self.E_TECurveLoadFilename.text())
        )
        self.E_BECurveEditButton.clicked.connect(
            lambda: self.csv_editor(self.E_BECurveLoadFilename.text())
        )
        self.D_TECurveEditButton.clicked.connect(
            lambda: self.csv_editor(self.D_TECurveLoadFilename.text())
        )
        self.D_BECurveEditButton.clicked.connect(
            lambda: self.csv_editor(self.D_BECurveLoadFilename.text())
        )

        # TODO PDF - See invoice_maker
        # self.printer = qtps.QPrinter()
        # self.printer.setOrientation(qtps.QPrinter.Portrait)
        # self.printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        #self.actionPrintToPDF.triggered.connect(self.export_pdf)

        # ? window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

    def path_extractor(self, dest):
        """Write CSV file path to destination"""
        my_path, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select a CSV file to load…",
            BASEDIR,
            'CSV Files (*.csv)',
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        dest.setText(my_path)

    def csv_editor(self, path):
        """Edit CSV file located in path"""
        if path:
            self.csveditor_screen = integrated_csv_editor.MainWindow()
            self.csveditor_screen.select_file(path)
            # ApplicationModal to block input in all windows
            self.csveditor_screen.setWindowModality(QtCore.Qt.ApplicationModal)
            self.csveditor_screen.setFocus(True)
            self.csveditor_screen.show()

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
                # TODO custom settings elements (no spaces):
                self.my_settings.setValue(str('My nice setting name'), bool('Tobedefined'))
                self.my_settings.sync()
                self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
            except Exception as e:
                qtw.QMessageBox.critical(self, 'Error', f"Could not save settings: {e}")

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
                    # TODO read custom settings elements in guirestore(no spaces)
                    self.my_settings.sync()
                    self.statusBar().showMessage("Changes being saved to: {}".format(self.filename))
                    self.setWindowTitle(os.path.basename(self.filename))
                except Exception or TypeError as e:
                    qtw.QMessageBox.critical(self, 'Error', f"Could not open settings: {e}")
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
                # TODO custom settings elements (no spaces):
                self.my_settings.setValue(str('My nice setting name'), bool('Tobedefined'))
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
        infoScreen.setText('RailwaySim is licenced under the GNU GPL.\t\t')
        infoScreen.setInformativeText("The complete license is available below.\t\t")
        try:
            infoScreen.setDetailedText(
                open(os.path.join(BASEDIR, "LICENSE"), "r", encoding="utf-8").read()
            )
        except:
            infoScreen.setDetailedText("http://www.gnu.org/licenses/gpl-3.0.en.html")
        infoScreen.setWindowModality(QtCore.Qt.ApplicationModal)
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
        self.darkIsChecked = self.cb_dark.isChecked()
        self.my_settings
        try:
            import qdarkstyle
            if not self.darkIsChecked:
                app.setStyleSheet("")
                window.iconFixes()
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())
                window.iconFixes(styleSheet=True)

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