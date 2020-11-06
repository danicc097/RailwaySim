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

import matplotlib.pyplot as plt
from custom_mpl_toolbar import MyMplToolbar
import custom_mpl_toolbar
from matplotlib.ticker import FixedLocator, FixedFormatter

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractButton, QDialog, QMainWindow, QWidget, QSizePolicy
from RailwaySim_GUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets as qtw
import os
from save_restore import guisave, guirestore, grab_GC
from RailwaySim_GUI_pref import Ui_Form
import integrated_csv_editor

from solver.data_formatter import s_to_hhmmss, hhmm_to_s
from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams, style
import random
import numpy as np
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
        self.instances_route_toolbar = []
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
        # ? destination widget as arg
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
        self.ProfileLoadButton.clicked.connect(self.create_route_plot)

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
        self.pref_screen = Preferences(self.GUI_preferences, self)
        self.iconFixes()  # change theme after Preferences settings are restored

        #? Embedded matplotlib in Route tab
        #! TO BE CALLED WHEN A FILE IS LOADED
    def create_route_plot(self):
        #* Delete previous instances if any
        try:
            self.instances_route_canvas[0].hide()
            self.instances_route_toolbar[0].hide()
            del self.instances_route_canvas[0]
            del self.instances_route_toolbar[0]
        except:
            pass
        self.route_canvas = PlotCanvas_route(self.GUI_preferences, self)
        darkMode = bool(int(self.GUI_preferences.value('cb_dark')))
        self.route_toolbar = Toolbar_route(
            self.route_canvas, self.route_canvas, coordinates=True, darkMode=darkMode
        )  # Do not set parent on this first widget - Prevents toolbar theme update
        self.verticalLayout_2.addWidget(self.route_canvas)
        self.verticalLayout_2.addWidget(self.route_toolbar)

        # ? Keep track of NavToolbar and Canvas
        self.instances_route_canvas.append(self.route_canvas)
        self.instances_route_toolbar.append(self.route_toolbar)

        # ? Route tab checkboxes
        self.cb_r_stations.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)
        self.cb_r_speedres.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)
        self.cb_r_grade.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)
        self.cb_r_profile.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)
        self.cb_r_radii.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)

    # TODO PDF - See invoice_maker
    # self.printer = qtps.QPrinter()
    # self.printer.setOrientation(qtps.QPrinter.Portrait)
    # self.printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
    # self.actionPrintToPDF.triggered.connect(self.export_pdf)

    #!######################################################################
    #! Non-__init__ methods below
    #!######################################################################

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
                    self.statusBar().showMessage(
                        "Changes now being saved to: {}".format(self.filename)
                    )
                    self.setWindowTitle(os.path.basename(self.filename))
                    #* Update plots
                    if self.ProfileLoadFilename is not None:
                        try:
                            self.instances_route_canvas[0].hide()
                            self.instances_route_toolbar[0].hide()
                            del self.instances_route_canvas[0]
                            del self.instances_route_toolbar[0]
                        except:
                            pass
                        self.create_route_plot()

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
            self.close()


class Toolbar_route(MyMplToolbar):
    def __init__(self, canvas, parent, coordinates, darkMode):
        super().__init__(canvas, parent, coordinates, darkMode)


# Need to define parent to access MainWindow widgets
class PlotCanvas_route(FigureCanvas):
    """Route input data graph"""
    def __init__(self, GUI, parent=None, dpi=100):
        # TODO param font lost on new window and updates
        self.GUI_preferences = GUI
        self.parent = parent
        self.route_fig = Figure(dpi=dpi)
        FigureCanvas.__init__(self, self.route_fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # * SOURCE DATA
        if self.parent.ProfileLoadFilename.text() is not None:
            self.ROUTE_INPUT_DF = np.genfromtxt(
                self.parent.ProfileLoadFilename.text(),
                delimiter=',',
                dtype=str,
                encoding='utf-8-sig',
                autostrip=True,
                deletechars="",
            )

            self.ROUTE_INPUT_DF = self.ROUTE_INPUT_DF.T
            self.distance = np.array(self.ROUTE_INPUT_DF[3][1:], dtype=float)
            self.kpoint = np.cumsum(self.distance / 1000, dtype=float)
            self.grade = np.array(self.ROUTE_INPUT_DF[4][1:], dtype=float)
            self.radii = np.array(self.ROUTE_INPUT_DF[5][1:], dtype=float)
            self.speed_res = np.array(self.ROUTE_INPUT_DF[6][1:], dtype=float)
            self.station_names = np.array(self.ROUTE_INPUT_DF[12][1:], dtype=str)
            self.profile = [0] * len(self.distance)
            for index, distance_step in enumerate(self.distance):
                if index < 1:
                    self.profile[index] = 0
                else:
                    self.profile[index] = distance_step * self.grade[index] / 1000 + self.profile[
                        index - 1]

            self.profile = np.array(self.profile)

            #TODO profile from grade and distance

            # * Timetable
            self.timetable_stations = np.array(
                [str(a) for a in self.ROUTE_INPUT_DF[0][1:] if a != ""]
            )
            self.timetable_stations_kpoint = np.array(
                [self.kpoint[index] for index, a in enumerate(self.distance) if a == 0]
            )
            try:
                self.timetable_dwell_time = np.array(
                    [int(a) for a in self.ROUTE_INPUT_DF[1][1:] if a != ""]
                )
            except:
                self.timetable_dwell_time = None
            try:
                self.timetable_arrival_time = np.array(
                    [hhmm_to_s(a) for a in self.ROUTE_INPUT_DF[2][1:] if a != ""]
                )
            except:
                self.timetable_arrival_time = None
            self.plot_route()

    def plot_route(self):

        #* ↓ OLD
        self.route_fig.clear()  # clear wrong format on graph init

        #? Setting theme
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

        #? Plot axes
        self.ax = self.route_fig.add_subplot(111)
        # self.ax.set_title('Very nice graph')
        self.ax.set_xlabel("Distance [km]")
        self.ax.set_ylabel("Speed [km/h]")
        self.line0, = self.ax.step(self.kpoint, self.speed_res, label="Speed [km/h]", where="pre")

        #* Twin axis x 2
        if self.parent.cb_r_grade.isChecked():
            self.line1, = self.ax.step(self.kpoint, self.grade, label="Grade [‰]", where="pre")

        if self.parent.cb_r_profile.isChecked():
            self.line3, = self.ax.plot(self.kpoint, self.profile, label="Profile [m]")

        #* Twin axis y - station tick marks
        if self.parent.cb_r_stations.isChecked():
            self.ax2 = self.ax.twiny()
            self.ax2.set_xlim(self.ax.get_xlim())
            self.ax2.set_label('Stations')
            self.ax2.tick_params(
                axis="x",
                which='major',
                direction="in",
                width=1.5,
                length=7,
                labelsize=10,
                color="red",
                rotation=20
            )
            x_locator = FixedLocator(self.timetable_stations_kpoint)
            x_formatter = FixedFormatter(self.timetable_stations)
            self.ax2.xaxis.set_major_locator(
                x_locator
            )  # it's best to first set the locator and only then the formatter
            self.ax2.xaxis.set_major_formatter(x_formatter)
            # ? optionally add vertical lines at each of the station positions
            for x in self.timetable_stations_kpoint:
                self.ax2.axvline(x, color='red', ls=':', lw=1.5)

        #* Twin axis x - Radii
        self.ax3 = self.ax.twinx()
        self.ax3.set_ylabel('Radii [m]')
        if self.parent.cb_r_radii.isChecked():
            self.line2, = self.ax3.step(self.kpoint, self.radii, label="Radii [m]", where="pre")
            self.line2.set_color("purple")
        # Line color has to be set during/after axis plot
        if self.dark_mode_set: self.line0.set_color("white")
        global watermark
        self.route_fig.text(
            0.5, 0.5, watermark, fontsize=20, color='gray', ha='center', va='center', alpha=0.6
        )

        handles, labels = [], []
        for ax in self.route_fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                handles.append(h)
                labels.append(l)

        self.ax.legend(handles, labels)
        self.draw()
        self.route_fig.set_tight_layout(True)  # Tight layout on start

    def route_canvas_checkbox_handler(self):
        self.plot_route()


class Preferences(QWidget, Ui_Form):
    """Preferences widget screen"""
    def __init__(self, GUI, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
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
        self.cb_dark_check()  # Restores dark mode on start

    def cb_dark_check(self):
        """Define stylesheet based on saved settings"""
        # * Save checkbox status after signal
        guisave(self, self.GUI_preferences)
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        # * Apply corresponding style
        try:
            import qdarkstyle
            if not self.dark_mode_set:
                app.setStyleSheet("")  # Default style
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())
            # * Update icons, toolbar and canvas
            for window in window_list:
                window.iconFixes()
        except:
            qtw.QMessageBox.critical(self, "Error", "Could not set all stylesheet settings.")
        if len(self.parent.instances_route_canvas) > 0:
            self.window_plot_update()

    def cb_watermark_check(self):
        """Define watermark based on checkbox state and line text"""
        self.text_watermark_check()
        for window in window_list:
            try:
                window.route_canvas.plot_route()
            except:
                pass
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
        for index, window in enumerate(window_list):
            window.iconFixes()
            # window.verticalLayout_2.removeWidget(window.route_canvas)
            # window.verticalLayout_2.removeWidget(window.route_toolbar)
            window.route_canvas = PlotCanvas_route(window.GUI_preferences, window)
            darkMode = bool(int(window.GUI_preferences.value('cb_dark')))
            window.route_toolbar = Toolbar_route(
                window.route_canvas, window.route_canvas, coordinates=True, darkMode=darkMode
            )  # Do not set parent on this first widget - Prevents toolbar theme update
            window.verticalLayout_2.addWidget(window.route_canvas)
            window.verticalLayout_2.addWidget(window.route_toolbar)
            window.instances_route_canvas.append(window.route_canvas)
            window.instances_route_toolbar.append(window.route_toolbar)
            print("WINDOW NUMBER {} IS : {}".format(index, window))
            print('window.instances_route_canvas :', window.instances_route_canvas)
            print('window.instances_route_toolbar :', window.instances_route_toolbar)
            if len(window.instances_route_toolbar) > 1:
                window.instances_route_canvas[0].hide()
                window.instances_route_toolbar[0].hide()
                del window.instances_route_canvas[0]
                del window.instances_route_toolbar[0]

            # TODO hide delete
            # # ? Hide or delete previous
            # # window.instances_route_canvas[0].setVisible(False)
            # if len(window.instances_route_toolbar) > 1:
            #     #     print(window.instances_route_toolbar)
            #     del window.instances_route_canvas[0]
            #     del window.instances_route_toolbar[0]
            # hide previous
            # a = window.instances_route_toolbar[-1]
            # a.setVisible(False)
            # a = window.instances_route_canvas[-1]
            # a.setVisible(False)
            #     print("after delete")
            # print("canvas", window.instances_route_canvas)
            # print("toolbars", window.instances_route_toolbar)

    def hide_preferences(self):
        """Exits Preferences window"""
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
