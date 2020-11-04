"""
Plotting possibilities: 
(pyinstaller supported) --> matplotlib, pandas , 
                        seaborn, ggplot2
! pipenv run python RailwaySim_main.py

! pyuic5 -x RailwaySim_GUI.ui -o RailwaySim_GUI.py 
! pyuic5 -x RailwaySim_GUI_pref.ui -o RailwaySim_GUI_pref.py
! pipenv run pyinstaller --onefile RailwaySim_main.py


# * ImageMagick icons: magick mogrify tranparent -channel RGB -negate *.png
"""

from custom_mpl_toolbar import MyMplToolbar

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractButton, QDialog, QMainWindow, QWidget, QSizePolicy
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw
import os
from save_restore import guisave, guirestore, grab_GC
from RailwaySim_GUI_pref import Ui_Form
import integrated_csv_editor

from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams, style
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

BASEDIR = os.path.dirname(__file__)

# TODO interpolate widget size upon resize

# TODO resize app based on resolution

# TODO read route INPUT


class NewWindow(QMainWindow):
    """MainWindow factory"""
    def __init__(self):
        super().__init__()
        global window_list
        window_list = []  # Allow multiple MainWindow instances
        # ? Preferences on program start
        GUI_preferences_path = os.path.join(BASEDIR, 'resources/GUI_preferences.ini')
        self.GUI_preferences = QtCore.QSettings(GUI_preferences_path, QtCore.QSettings.IniFormat)
        self.add_new_window()

    def add_new_window(self):
        """Create now MainWindow instance"""
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
        self.instances_route_canvas = []
        self.instances_toolbar_canvas = []
        self.statusBar().showMessage(BASEDIR)
        self._buttonEdits()
        self.mainEdits()

    def iconFixes(self):
        '''Selects icon files for current stylesheet'''
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

    def _buttonEdits(self):
        """Adds functionality to buttons"""
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
        self.E_TECurveLoadButton.setToolTip('Import CSV file')
        self.E_BECurveLoadButton.setToolTip('Import CSV file')
        self.D_TECurveLoadButton.setToolTip('Import CSV file')
        self.D_BECurveLoadButton.setToolTip('Import CSV file')
        self.ProfileLoadButton.setToolTip('Import CSV file')

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
        self.E_TECurveEditButton.setToolTip('Edit CSV file')
        self.E_BECurveEditButton.setToolTip('Edit CSV file')
        self.D_TECurveEditButton.setToolTip('Edit CSV file')
        self.D_BECurveEditButton.setToolTip('Edit CSV file')
        self.ProfileEditButton.setToolTip('Edit CSV file')

    def mainEdits(self):
        """MainWindow GUI changes"""
        # ? Disable window resizing
        #self.setFixedSize(self.size())

        # ? PushButtons
        self.StartSimButton.clicked.connect(self.start_simulation)

        # ? Toolbar buttons
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionAbout.triggered.connect(self.AboutInfo)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit.triggered.connect(self.show_preferences)

        # ? open and save triggers
        # WindowShortcut context is required with multiple windows
        self.actionNew_Window.triggered.connect(self.window.add_new_window)
        self.actionOpen.triggered.connect(self.readFile)
        self.actionSave.triggered.connect(self.writeFile)
        self.actionSave_as.triggered.connect(self.writeNewFile)

        # ? window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

        #? Instantiate and restore theme preferences
        self.pref_screen = Preferences(self.GUI_preferences)
        self.iconFixes()  # change theme after Preferences settings are restored

        #? Checkboxes based on graph in Route tab
        # self.horizontalLayout_checkboxes = qtw.QHBoxLayout(self.groupBox_15)
        # self.cb_ax_stations = qtw.QCheckBox(self.RouteTab)
        # self.horizontalLayout_checkboxes.addWidget(self.cb_ax_stations)
        # self.cb_ax_stations.setText('Stations')

        #? Embedded matplotlib in Route tab
        self.route_canvas = PlotCanvas_route(self.GUI_preferences)
        darkMode = bool(int(self.GUI_preferences.value('cb_dark')))
        self.route_toolbar = Toolbar_route(
            self.route_canvas, None, coordinates=True, darkMode=darkMode
        )  # Do not set parent on this first widget - Prevents toolbar theme update
        self.verticalLayout_2.addWidget(self.route_canvas)
        self.verticalLayout_2.addWidget(self.route_toolbar)

        # ? Keep track of NavToolbar and Canvas
        self.instances_route_canvas.append(self.route_canvas)
        self.instances_toolbar_canvas.append(self.route_toolbar)

        # TODO PDF - See invoice_maker
        # self.printer = qtps.QPrinter()
        # self.printer.setOrientation(qtps.QPrinter.Portrait)
        # self.printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        # self.actionPrintToPDF.triggered.connect(self.export_pdf)

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

    def writeNewFile(self):  # ? Save as
        """Saves GUI user input to a new config file"""
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
        """Restores GUI user input from a config file"""
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
        """Saves GUI user input to the previously opened config file"""
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
        """Shows license information"""
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
        close = qtw.QMessageBox(qtw.QMessageBox.Question, 'Exit', 'Exit application?', parent=self)
        close_reject = close.addButton('No', qtw.QMessageBox.NoRole)
        close_accept = close.addButton('Yes', qtw.QMessageBox.AcceptRole)
        close.exec()  # Necessary for property-based API
        if close.clickedButton() == close_accept:
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


class Toolbar_route(MyMplToolbar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlotCanvas_route(FigureCanvas):
    """Route input data graph"""
    def __init__(self, GUI, dpi=100):
        # TODO param font lost on new window and updates
        self.GUI_preferences = GUI
        self.route_fig = Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.route_fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        self.route_fig.clear()  # clear wrong format on graph init
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        if self.dark_mode_set:
            self.route_fig.patch.set_facecolor(
                (0.09803921569, 0.13725490196, 0.17647058824)
            )  # light grey
            rcParams['axes.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)  # dark grey
            rcParams['text.color'] = rcParams['axes.labelcolor'] = rcParams[
                'axes.edgecolor'] = rcParams['xtick.color'] = rcParams['ytick.color'] = 'white'
            rcParams['savefig.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)
        else:
            style.use('default')
            self.route_fig.patch.set_facecolor('white')
        rcParams['savefig.dpi'] = 300
        rcParams['font.family'] = 'Euclid'

        data = [random.random() for i in range(50)]
        self.ax = self.figure.add_subplot(111)
        self.line0, = self.ax.plot(data, 'r-', linewidth=0.5)
        self.ax.set_title('PyQt Matplotlib Example')
        # Line color has to be set during/after axis plot
        if self.dark_mode_set: self.line0.set_color("white")
        global watermark
        self.route_fig.text(
            0.5, 0.5, watermark, fontsize=20, color='gray', ha='center', va='center', alpha=0.5
        )
        self.draw()

        #TODO checkbuttons to show or hide
        # self.cb_r_stations.setText(_translate("MainWindow", "Stations"))
        # self.cb_r_speedres.setText(_translate("MainWindow", "Speed restriction"))
        # self.cb_r_grade.setText(_translate("MainWindow", "Grade"))
        # self.cb_r_profile.setText(_translate("MainWindow", "Profile"))
        # self.cb_r_radii.setText(_translate("MainWindow", "Curve radii"))


class Preferences(QWidget, Ui_Form):
    """Preferences widget screen"""
    def __init__(self, GUI):
        super().__init__()
        self.setupUi(self)
        self.GUI_preferences = GUI
        try:
            guirestore(self, self.GUI_preferences)
        except:  # Create new empty file if none found
            guisave(self, self.GUI_preferences)
        global watermark
        watermark = self.watermark.text()
        self.pushButton.clicked.connect(self.hide_preferences)
        self.cb_dark.stateChanged.connect(self.cb_dark_check)
        self.cb_watermark.stateChanged.connect(self.cb_watermark_check)
        self.cb_dark_check()

    def cb_dark_check(self):
        """Define stylesheet based on saved settings"""
        guisave(self, self.GUI_preferences)
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        try:
            import qdarkstyle
            if not self.dark_mode_set:
                app.setStyleSheet("")  # Default style
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())
            self.window_plot_update()

        except:
            qtw.QMessageBox.critical(self, "Error", "Could not set all stylesheet settings.")

    def cb_watermark_check(self):
        """Define watermark based on checkbox state and line text"""
        self.text_watermark_check()
        for window in window_list:
            window.route_canvas.plot()
        guisave(self, self.GUI_preferences)

    def text_watermark_check(self):
        """Save watermark QLineEdit text"""
        global watermark
        if self.cb_watermark.isChecked():
            watermark = self.watermark.text()
        else:
            watermark = ""

    def window_plot_update(self):
        """Update icons and replot"""
        for window in window_list:
            window.iconFixes()
            try:
                # del window.route_toolbar
                # rcParams['toolbar'] = 'None'
                window.route_toolbar = None
                # window.verticalLayout_2.removeWidget(window.route_toolbar)
            except:
                pass

            window.route_toolbar = Toolbar_route(
                window.route_canvas, None, coordinates=True, darkMode=self.dark_mode_set
            )
            window.route_canvas = PlotCanvas_route(window.GUI_preferences)
            window.route_canvas.plot()
            # window.verticalLayout_2.addWidget(window.route_toolbar)

            window.instances_route_canvas.append(window.route_canvas)
            window.instances_toolbar_canvas.append(window.route_toolbar)
            # ? Hide or delete previous
            # window.instances_route_canvas[:-1].setVisible(False)
            if len(window.instances_toolbar_canvas) > 1:
                print(window.instances_route_canvas)
                # del window.instances_route_canvas[:-1]
                # del window.instances_toolbar_canvas[:-1]
                # hide previous
                a = window.instances_toolbar_canvas[-1]
                a.setVisible(False)
                a = window.instances_route_canvas[-1]
                a.setVisible(False)
                print("after delete")
            print("canvas", window.instances_route_canvas)
            print("toolbars", window.instances_toolbar_canvas)

    def hide_preferences(self):
        """Exits Preferences window"""
        self.text_watermark_check()
        self.cb_watermark_check()
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
