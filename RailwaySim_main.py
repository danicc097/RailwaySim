"""
Plotting possibilities: 
(pyinstaller supported) --> matplotlib, pandas , 
                        seaborn, ggplot2

! pipenv run python RailwaySim_main.py

! pyuic5 -x RailwaySim_GUI.ui -o RailwaySim_GUI.py 
! pyuic5 -x RailwaySim_GUI_pref.ui -o RailwaySim_GUI_pref.py
! pipenv run pyinstaller --onefile RailwaySim_main.py

"""
import configparser
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QPalette
import PyQt5.QtPrintSupport as qtps
from PyQt5.QtWidgets import QDialog, QMainWindow, QWidget, QSizePolicy
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw, uic
import os
from save_restore import guisave, guirestore, grab_GC
from RailwaySim_GUI_pref import Ui_Form
import integrated_csv_editor

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

BASEDIR = os.path.dirname(__file__)

# TODO interpolate widget size upon resize

# TODO resize app based on resolution

# TODO center new windows based on mainWindow current location

# TODO new .ini file for theme preference on startup


class NewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global window_list
        window_list = []  # Allow multiple MainWindow instances
        # Create Preferences on program start
        GUI_preferences_path = os.path.join(BASEDIR, 'resources/GUI_preferences.ini')
        self.GUI_preferences = QtCore.QSettings(GUI_preferences_path, QtCore.QSettings.IniFormat)
        self.add_new_window()

    def add_new_window(self):
        window = MainWindow(self, self.GUI_preferences)
        window_list.append(window)
        window.show()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, window, GUI):
        super().__init__()
        self.setupUi(self)
        self.window = window
        self.GUI_preferences = GUI
        self.config_is_set = 0  # Call tracker
        self.statusBar().showMessage(BASEDIR)

        #self.iconFixes()
        self.mainEdits()

    # TODO dark mode replace "_dark.png"
    def iconFixes(self):
        print('iconFixes was called')
        global darkPath
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        if not self.dark_mode_set:
            darkPath = 'resources/images/'
        if self.dark_mode_set:
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
        self.ProfileEditButton.setIcon(icon_edit)
        self.ProfileLoadButton.setIcon(icon_import)

    def mainEdits(self):
        # ? Disable window resizing
        #self.setFixedSize(self.size())

        # ? PushButton
        self.StartSimButton.clicked.connect(self.start_simulation)

        # ? Toolbar button actions
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionAbout.triggered.connect(self.AboutInfo)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit.triggered.connect(self.show_preferences)

        # ? open and save triggers
        # WindowShortcut context is required
        self.actionNew_Window.triggered.connect(self.window.add_new_window)
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
        self.ProfileLoadButton.clicked.connect(
            lambda: self.path_extractor(self.ProfileLoadFilename)
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
        self.ProfileEditButton.clicked.connect(
            lambda: self.csv_editor(self.ProfileLoadFilename.text())
        )

        #? Embedded matplotlib in Route tab
        self.route_canvas = PlotCanvas(self.GUI_preferences, width=10, height=8)
        self.route_toolbar = NavigationToolbar(self.route_canvas, self)
        self.verticalLayout_2.addWidget(self.route_toolbar)
        self.verticalLayout_2.addWidget(self.route_canvas)

        # TODO PDF - See invoice_maker
        # self.printer = qtps.QPrinter()
        # self.printer.setOrientation(qtps.QPrinter.Portrait)
        # self.printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        #self.actionPrintToPDF.triggered.connect(self.export_pdf)

        # ? window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

        # Instantiate and restore theme preferences
        self.pref_screen = Preferences(self.GUI_preferences)
        # guirestore(self.pref_screen, self.GUI_preferences)
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        print('dark_mode_set: ', self.dark_mode_set)
        self.iconFixes()
        # self.route_canvas.plot_theme_update() #* update in class

    def show_preferences(self):
        """Shows the Preferences widget"""
        # ApplicationModal to block input in all windows
        self.pref_screen.setWindowModality(QtCore.Qt.ApplicationModal)
        self.pref_screen.setFocus(True)
        guirestore(self.pref_screen, self.GUI_preferences)
        self.pref_screen.show()

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

    # @pyqtSlot()
    # def newFile(self):
    #     """Creates new empty MainWindow instance"""
    #     # * No restriction on the number of QMainWindow instances
    #     # ! Limitation of one QApplication per process
    #     win = NewWindow()
    #     win.show()
    #     self.window.append(win)

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
                # all values will be returned as QString
                guisave(self, self.my_settings)
                # TODO custom settings elements (no spaces):
                self.my_settings.setValue(str('Custom_setting_name'), bool('Tobedefined'))
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
            else:
                self.writeNewFile()
        else:
            self.writeNewFile()

    # ? capture data
    # def ShowMessage(self):
    #     # myNumber = self.TIME_STEP.cleanText()
    #     # qtw.QMessageBox.information(self, 'The number is:', myNumber)

    def AboutInfo(self):
        self.infoScreen = qtw.QMessageBox(self)  # Pass self to QMessageBox
        self.infoScreen.setWindowTitle('Legal Information')
        self.infoScreen.setText('RailwaySim is licenced under the GNU GPL.\t\t')
        self.infoScreen.setInformativeText("The complete license is available below.\t\t")
        # self.infoScreen.closeEvent()
        try:
            self.infoScreen.setDetailedText(
                open(os.path.join(BASEDIR, "LICENSE"), "r", encoding="utf-8").read()
            )
        except:
            self.infoScreen.setDetailedText("http://www.gnu.org/licenses/gpl-3.0.en.html")
        self.infoScreen.setWindowModality(QtCore.Qt.ApplicationModal)
        self.infoScreen.show()

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

    def start_simulation(self):
        runSim = qtw.QMessageBox.question(
            self, "Start simulation", "Start simulation?\nAll changes will be saved locally.",
            qtw.QMessageBox.Yes | qtw.QMessageBox.No
        )
        if runSim == qtw.QMessageBox.Yes:
            try:
                self.writeFile()
                print('Changes saved')
                # import solver.shortest_operation as s_o
                # s_o.run(self.my_settings)
                grab_GC(self.my_settings)
            except:
                print('Failed')
        else:
            self.close


class PlotCanvas(FigureCanvas):
    def __init__(self, GUI, parent=None, width=10, height=8, dpi=100):
        # plt.style.use('dark_background')
        # plt.style.use('default')
        self.GUI_preferences = GUI
        self.route_fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.route_fig)
        # self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot_theme_update()
        self.plot()

    def plot(self):
        data = [random.random() for i in range(250)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-', linewidth=0.5)
        ax.set_title('PyQt Matplotlib Example')
        self.draw()

    def plot_theme_update(self):
        print('plot_theme_update was called')
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        if self.dark_mode_set:
            self.route_fig.patch.set_facecolor(
                (0.09803921569, 0.13725490196, 0.17647058824)
            )  # light grey
            plt.rcParams['axes.facecolor'] = (
                0.19607843137, 0.25490196078, 0.29411764706
            )  # dark grey
            self.COLOR = 'white'
            plt.rcParams['text.color'] = self.COLOR
            plt.rcParams['axes.labelcolor'] = self.COLOR
            plt.rcParams['axes.edgecolor'] = self.COLOR
            plt.rcParams['xtick.color'] = self.COLOR
            plt.rcParams['ytick.color'] = self.COLOR
        else:
            plt.style.use('default')
            self.route_fig.patch.set_facecolor('white')


# TODO QLineEdit is not restored. Deleted on new app init


class Preferences(QWidget, Ui_Form):
    """Preferences widget screen"""
    def __init__(self, GUI):
        super().__init__()
        self.setupUi(self)
        self.GUI_preferences = GUI
        guirestore(self, self.GUI_preferences)
        print('Preferences instantiated')
        print([(key, self.GUI_preferences.value(key)) for key in self.GUI_preferences.allKeys()])
        self.pushButton.clicked.connect(self.hide_preferences)
        self.cb_dark.stateChanged.connect(self.cb_dark_check)
        self.cb_watermark.stateChanged.connect(self.cb_watermark_check)

    def cb_dark_check(self):
        """Define stylesheet based on checkbox state"""
        print('cb_dark_check accessed')
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        try:
            import qdarkstyle
            checked = bool(int(self.GUI_preferences.value('cb_dark')))
            print('checked is', checked)
            if not checked:
                app.setStyleSheet("")  # Default style
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())
            for window in window_list:
                self.window = window

                print('cb_dark_check\'s dark_mode_set: ', self.dark_mode_set)
                self.window.iconFixes()
                self.window.route_canvas.plot_theme_update()
        except:
            qtw.QMessageBox.critical(self, "Error", "Could not set all stylesheet settings.")
        guisave(self, self.GUI_preferences)

    def cb_watermark_check(self):
        print('cb_watermark_check accessed')
        guisave(self, self.GUI_preferences)
        """Define watermark based on checkbox state and line text"""

    def hide_preferences(self):
        guisave(self, self.GUI_preferences)
        self.hide()


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
    w = NewWindow()  # Instantiate window factory class

    # ? Exit with Ctrl + C
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec_())
