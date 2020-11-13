"""
! pipenv run python RailwaySim_main.py
! pyuic5 -x RailwaySim_GUI.ui -o RailwaySim_GUI.py 
! pyuic5 -x RailwaySim_GUI_pref.ui -o RailwaySim_GUI_pref.py
! pipenv run pyinstaller --onefile RailwaySim_main.py

# * ImageMagick icons: magick mogrify tranparent -channel RGB -negate *.png

# * Known/suspected bugs, nuisances → 

# TODO:
    Desktop>System tray notifications:
    - D:\OneDrive\Coding\Python\GUIs\examples-_\examples-_\src\pyqt-official\desktop\systray

    MORE OPEN/SAVE LOGIC:
    -  D:\OneDrive\Coding\Python\GUIs\examples-_\examples-_\src\pyqt-official\mainwindows\recentfiles.py

    PRINTING:
    - D:\OneDrive\Coding\Python\GUIs\examples-_\examples-_\src\pyqt-official\mainwindows\dockwidgets\dockwidgets.py


"""

import os
import random
import ctypes

import matplotlib.pyplot as plt
import numpy as np
import qdarkstyle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams, style
from matplotlib.ticker import FixedFormatter, FixedLocator
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAbstractButton, QDialog, QMainWindow, QSizePolicy, QWidget, QSystemTrayIcon
)

# cwd
import integrated_csv_editor
from custom_mpl_toolbar import MyMplToolbar
from RailwaySim_GUI import Ui_MainWindow
from RailwaySim_GUI_pref import Ui_Form
from save_restore import grab_GC, guirestore, guisave
from scaled_labels import ScaledLabel, label_grabber
from solver.data_formatter import hhmm_to_s, s_to_hhmmss

from solver.shortest_operation import ShortestOperationSolver

BASEDIR = os.path.dirname(__file__)

#* Allow multiple MainWindow instances
window_list = []
SEP = os.path.sep

# set icon on Windows
myappid = 'RailwaySim.v0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class NewWindow(QMainWindow):
    """MainWindow factory"""
    def __init__(self):
        super().__init__()
        #* Preferences load on program start
        GUI_preferences_path = os.path.join(BASEDIR, 'resources/GUI_preferences.ini')
        self.GUI_preferences = QtCore.QSettings(GUI_preferences_path, QtCore.QSettings.IniFormat)
        self.add_new_window()

    def add_new_window(self):
        """Create now MainWindow instance"""
        window = MainWindow(self, self.GUI_preferences)
        app_icon = QIcon()
        app_icon_path = BASEDIR + SEP + 'resources' + SEP + 'images' + SEP + 'RailwaySimIcon.png'
        app_icon.addFile(app_icon_path)
        app.setWindowIcon(app_icon)
        window.setWindowIcon(app_icon)
        window_list.append(window)
        window.show()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, window, GUI):
        super().__init__()
        self.setupUi(self)
        self.windowManager = window
        self.GUI_preferences = GUI
        self.config_is_set = 0  # Call tracker for config file
        self.instances_route_canvas = []
        self.instances_route_toolbar = []
        self.statusBar().showMessage(BASEDIR)
        self._buttonEdits()
        self._mainEdits()

    def _iconFixes(self):
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
        #* CSV import buttons - anon to prevent autostart
        #* "clicked" emits a signal (checked) when pressed:
        #* checkvoid QAbstractButton::clicked(bool checked = false)

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
        self.ProfileLoadButton.clicked.connect(self.setup_route_checkbuttons)

        self.E_TECurveLoadButton.setToolTip('Import CSV file')
        self.E_BECurveLoadButton.setToolTip('Import CSV file')
        self.D_TECurveLoadButton.setToolTip('Import CSV file')
        self.D_BECurveLoadButton.setToolTip('Import CSV file')
        self.ProfileLoadButton.setToolTip('Import CSV file')

        #* CSV edit buttons
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

    def _mainEdits(self):
        """MainWindow GUI changes"""
        #* PushButtons
        self.StartSimButton.clicked.connect(self.start_simulation)

        #* Toolbar buttons
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionAbout.triggered.connect(self.AboutInfo)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit.triggered.connect(self.show_preferences)

        #* open and save triggers
        # WindowShortcut context is required with multiple windows
        self.actionNew_Window.triggered.connect(self.windowManager.add_new_window)
        self.actionOpen.triggered.connect(self.readFile)
        self.actionSave.triggered.connect(self.writeFile)
        self.actionSave_as.triggered.connect(self.writeNewFile)

        #* Instantiate and restore theme preferences on window start
        self.pref_screen = Preferences(self.GUI_preferences, self)
        self._iconFixes()  # change icons after Preferences are restored

        #* Spacer for empty Route tab
        self.spacerItem = qtw.QSpacerItem(
            20, 40, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Expanding
        )
        self.verticalLayout_2.addItem(self.spacerItem)

        #* Loco or passenger train simulation selection
        self.gb_locomotive.toggled.connect(
            lambda checked: checked and self.gb_passenger.setChecked(False)
            if self.gb_passenger.isChecked() else checked
        )
        self.gb_passenger.toggled.connect(
            lambda checked: checked and self.gb_locomotive.setChecked(False)
            if self.gb_locomotive.isChecked() else checked
        )

        #* window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

    def create_route_plot(self):
        """Route canvas and toolbar creator. Called when a file is loaded"""
        if self.ProfileLoadFilename.text() != "":
            #* Delete vertical spacer
            self.verticalLayout_2.removeItem(self.spacerItem)
            #* Delete previous instances if any
            try:
                self.instances_route_canvas[0].hide()
                self.instances_route_toolbar[0].hide()
                del self.instances_route_canvas[0]
                del self.instances_route_toolbar[0]
            except:
                pass
            #* Create new instances of canvas and toolbar
            if len(self.ProfileLoadFilename.text()) > 3:
                self.route_canvas = PlotCanvas_route(self.GUI_preferences, self)
                darkMode = bool(int(self.GUI_preferences.value('cb_dark')))
                self.route_toolbar = MyMplToolbar(
                    self.route_canvas, self.route_canvas, coordinates=True, darkMode=darkMode
                )
                self.verticalLayout_2.addWidget(self.route_canvas)
                self.verticalLayout_2.addWidget(self.route_toolbar)

                #* Keep track of NavToolbar and Canvas
                self.instances_route_canvas.append(self.route_canvas)
                self.instances_route_toolbar.append(self.route_toolbar)
                self.statusBar().showMessage("Loaded {}.".format(self.ProfileLoadFilename.text()))

        else:
            self.statusBar().showMessage("Could not plot because no data was selected.")

    def setup_route_checkbuttons(self):
        """Route tab checkboxes. Must be called after each plot update."""
        if self.ProfileLoadFilename.text() != "":
            try:
                if self.route_canvas is not None:
                    self.cb_r_stations.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
                    self.cb_r_speedres.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
                    self.cb_r_grade.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
                    self.cb_r_profile.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
                    self.cb_r_radii.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
                    self.cb_r_legend.stateChanged.connect(
                        self.route_canvas.route_canvas_checkbox_handler
                    )
            except Exception as e:
                self.statusBar().showMessage(
                    "Could not setup checkboxes: \n" + str(e) + "\n Try again or reload the data"
                )

    # TODO: PDF - See invoice_maker and qtdemo
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
        if my_path == "":
            qtw.QMessageBox.critical(
                self, "Operation aborted", "Empty filename or none selected. \n Please try again.",
                qtw.QMessageBox.Ok
            )
            self.statusBar().showMessage("Select a valid CSV file")
        else:
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
                self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
            except Exception as e:
                qtw.QMessageBox.critical(self, 'Error', f"Could not save settings: {e}")

    def readFile(self):  # ? Open
        """Restores GUI user input from a config file"""
        #* File dialog
        self.filename, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select a configuration file to load…",
            BASEDIR,
            'Configuration Files (*.ini)',
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        #* Invalid file or none
        if self.filename == "":
            qtw.QMessageBox.critical(
                self, "Operation aborted", "Empty filename or none selected. \n Please try again.",
                qtw.QMessageBox.Ok
            )
            self.statusBar().showMessage("Select a valid configuration file")
        #* Valid file
        else:
            if self.filename.lower().endswith('.ini'):
                self.config_is_set += 1
                try:
                    self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
                    guirestore(self, self.my_settings)
                    self.statusBar().showMessage(
                        "Changes now being saved to: {}".format(self.filename)
                    )
                    self.setWindowTitle(os.path.basename(self.filename))

                    #* Update route plot if a path was loaded from settings
                    if len(self.ProfileLoadFilename.text()) > 3:
                        try:
                            self.instances_route_canvas[0].hide()
                            self.instances_route_toolbar[0].hide()
                            del self.instances_route_canvas[0]
                            del self.instances_route_toolbar[0]
                        except:
                            pass
                        self.create_route_plot()
                        self.setup_route_checkbuttons()

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
                # self.my_settings.setValue(str('Nice_setting_name'), str('Tobedefined'))
            else:
                self.writeNewFile()
        else:
            self.writeNewFile()

    def AboutInfo(self):
        """Shows license information"""
        self.infoScreen = qtw.QMessageBox(None)
        self.infoScreen.setWindowTitle('Legal Information')
        self.infoScreen.setText('RailwaySim is licenced under the GNU GPL.\t\t')
        self.infoScreen.setInformativeText("The complete license is available below.\t\t")
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
        """Saves changes and runs the selected solver"""
        if not self.config_is_set:
            runSim = qtw.QMessageBox.question(
                self, "Start simulation",
                "Start simulation?\nAll changes will be saved locally first.",
                qtw.QMessageBox.Yes | qtw.QMessageBox.No
            )
        else:
            runSim = qtw.QMessageBox.question(
                self, "Start simulation",
                "Start simulation?\nAll changes will now be saved to \n{}.".format(self.filename),
                qtw.QMessageBox.Yes | qtw.QMessageBox.No
            )
        if runSim == qtw.QMessageBox.Yes:
            try:
                #TODO:
                self.writeFile()
                #* Save current window's user input to dict
                constants = grab_GC(self, self.my_settings)
                #* Compute and outputs a CSV
                ShortestOperationSolver(self, constants)
                #* Change to simulation tab and plot

            except Exception as e:
                qtw.QMessageBox.critical(self, "An error ocurred: ", str(e))
        else:
            pass


class PlotCanvas_route(FigureCanvas):
    """Route input data graph"""
    def __init__(self, GUI, parent, dpi=100):
        self.GUI_preferences = GUI
        self.parent = parent  # pass MainWindow to access its widgets
        self.route_fig = Figure(dpi=dpi)  # 100 dpi recommended
        FigureCanvas.__init__(self, self.route_fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.route_data_import()
        self.counter = 0  # Allow for plot retries upon exception

    def route_data_import(self):
        """Route profile data import."""
        if len(self.parent.ProfileLoadFilename.text()) > 3:
            self.ROUTE_INPUT_DF = np.genfromtxt(
                self.parent.ProfileLoadFilename.text(),
                delimiter=',',
                dtype=str,
                encoding='utf-8-sig',
                autostrip=True,
                deletechars="",
            )

            self.ROUTE_INPUT_DF = self.ROUTE_INPUT_DF.T

            try:
                self.distance = np.array(self.ROUTE_INPUT_DF[3][1:], dtype=float)
                self.kpoint = np.cumsum(self.distance / 1000, dtype=float)
                self.grade = np.array(self.ROUTE_INPUT_DF[4][1:], dtype=float)
                self.radii = np.array(self.ROUTE_INPUT_DF[5][1:], dtype=float)
                self.speed_res = np.array(self.ROUTE_INPUT_DF[6][1:], dtype=float)
                self.station_names = np.array(self.ROUTE_INPUT_DF[12][1:], dtype=str)

                #* Initialize profile array
                self.profile = np.zeros(len(self.distance), dtype=float)

                #* Calculate profile height from distance steps and grade
                for index, distance_step in enumerate(self.distance):
                    if index < 1:
                        self.profile[index] = 0
                    else:
                        self.profile[
                            index] = distance_step * self.grade[index] / 1000 + \
                                self.profile[index-1]
                # * Timetable
                self.timetable_stations = np.array(
                    [str(a) for a in self.ROUTE_INPUT_DF[0][1:] if a != ""]
                )
                # * Find station kilometric points (0 m travelled paths)
                self.timetable_stations_kpoint = np.array(
                    [self.kpoint[index] for index, a in enumerate(self.distance) if a == 0]
                )
                # * Optional timetable
                try:
                    self.timetable_dwell_time = np.array(
                        [int(a) for a in self.ROUTE_INPUT_DF[1][1:] if a != ""]
                    )
                except:
                    self.timetable_dwell_time = None
                # * Optional timetable
                try:
                    self.timetable_arrival_time = np.array(
                        [hhmm_to_s(a) for a in self.ROUTE_INPUT_DF[2][1:] if a != ""]
                    )
                except:
                    self.timetable_arrival_time = None

                self.plot_route()
            except:
                #* Attempt to replot once
                try:
                    if self.counter == 0:
                        self.route_data_import()
                        self.counter += 1
                except:
                    pass

    def plot_route(self):
        """Canvas and toolbar creation, deleting previous instances."""
        if len(self.parent.instances_route_toolbar) > 1:
            self.parent.instances_route_canvas[0].hide()
            self.parent.instances_route_toolbar[0].hide()
            del self.parent.instances_route_canvas[0]
            del self.parent.instances_route_toolbar[0]

        self.route_fig.clear()  # clear wrong format if any on graph init

        #* Setting theme
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

        #* Plot axes
        self.ax = self.route_fig.add_subplot(111)
        self.ax.set_xlabel("Distance [km]")
        self.ax.set_ylabel("Speed [km/h]")

        #* Plotting on main axis sharing X
        if self.parent.cb_r_speedres.isChecked():
            self.line0, = self.ax.step(
                self.kpoint, self.speed_res, label="Speed [km/h]", where="pre"
            )

        if self.parent.cb_r_grade.isChecked():
            self.line1, = self.ax.step(self.kpoint, self.grade, label="Grade [‰]", where="pre")

        if self.parent.cb_r_profile.isChecked():
            self.line3, = self.ax.plot(self.kpoint, self.profile, label="Profile [m]")

        #* Twin axis Y - station tick marks
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
            #* optionally add vertical lines at each of the station positions
            for x in self.timetable_stations_kpoint:
                self.ax2.axvline(x, color='red', ls=':', lw=1.5)

        #* Twin axis X - Radii
        if self.parent.cb_r_radii.isChecked():
            self.ax3 = self.ax.twinx()
            self.ax3.set_label('Distance [km] - Radii [m]')
            self.ax3.set_ylabel('Radii [m]')
            self.ax3.set_ylim(top=np.amax(self.radii) * 4, bottom=0)
            self.line2, = self.ax3.step(self.kpoint, self.radii, label="Radii [m]", where="pre")
            self.line2.set_color("purple")

        #* Line color has to be set during/after axis plot
        if self.dark_mode_set: self.line0.set_color("white")

        #* Include watermark if any
        global watermark
        self.route_fig.text(
            0.5, 0.5, watermark, fontsize=20, color='gray', ha='center', va='center', alpha=0.6
        )

        #* Include chart legend if checked
        if self.parent.cb_r_legend.isChecked():
            handles, labels = [], []
            for ax in self.route_fig.axes:
                for h, l in zip(*ax.get_legend_handles_labels()):
                    handles.append(h)
                    labels.append(l)
            self.ax.legend(handles, labels)

        self.draw()
        self.route_fig.set_tight_layout(True)  # Tight layout on start

    def route_canvas_checkbox_handler(self):
        """Replot on checkbox state change."""
        try:
            self.plot_route()
        except:
            pass
        # except Exception as e:
        #     qtw.QMessageBox.critical(
        #         self, "Error",
        #         str(e) + "\nCould not plot, please reload the data."
        #     )


class Preferences(QWidget, Ui_Form):
    """Preferences widget screen. Initialized alongside window."""
    def __init__(self, GUI, parent=None):
        super().__init__()
        self.setupUi(self)

        #* Optional param to access attributes
        self.parent = parent

        #* Restore latest .ini GUI config
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

        #* Restores dark mode on start
        self.cb_dark_check()

    def cb_dark_check(self):
        """Define stylesheet based on saved settings"""

        # * Save checkbox status after signal
        guisave(self, self.GUI_preferences)
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))

        try:
            # * Apply corresponding style
            if not self.dark_mode_set:
                app.setStyleSheet("")  # Default Fusion style
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())

            # * Update icons
            for window in window_list:
                window._iconFixes()

            # * Update plot
            self.window_plot_update()

        except:
            qtw.QMessageBox.critical(self, "Error", "Could not set all stylesheet settings.")

    def cb_watermark_check(self):
        """Define watermark based on checkbox state and line text"""
        global watermark
        if self.cb_watermark.isChecked():
            watermark = self.watermark.text()
        else:
            watermark = ""

        #* Redraw canvas application-wide
        for window in window_list:
            try:
                window.route_canvas.plot_route()
            except:
                pass
        guisave(self, self.GUI_preferences)

    def window_plot_update(self):
        """Update icons and replot in all windows"""
        for index, window in enumerate(window_list):
            window._iconFixes()
            window.route_canvas = PlotCanvas_route(window.GUI_preferences, window)
            darkMode = bool(int(window.GUI_preferences.value('cb_dark')))
            window.route_toolbar = MyMplToolbar(
                window.route_canvas, window.route_canvas, coordinates=True, darkMode=darkMode
            )
            window.verticalLayout_2.addWidget(window.route_canvas)
            window.verticalLayout_2.addWidget(window.route_toolbar)
            window.instances_route_canvas.append(window.route_canvas)
            window.instances_route_toolbar.append(window.route_toolbar)

            #* Keep only one canvas and toolbar in memory
            #* Delete blank charts where no file was selected (len == 1)
            if len(window.instances_route_toolbar) > 0:
                window.instances_route_canvas[0].hide()
                window.instances_route_toolbar[0].hide()
                del window.instances_route_canvas[0]
                del window.instances_route_toolbar[0]

    def hide_preferences(self):
        """Exits Preferences window"""
        self.cb_watermark_check()
        try:
            for window in window_list:
                window.setup_route_checkbuttons()  # Must be called every replot
        except:
            pass
        self.hide()


# TODO: QMovie animation simulation
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

    #* Exit with Ctrl + C
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    sys.exit(app.exec_())
