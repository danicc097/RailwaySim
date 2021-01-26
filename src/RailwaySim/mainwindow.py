"""
                 _-====-__-======-__-========-_____-============-__
                (                                                 _)
               (    _ __           _                  __,           )
             o (_  ( /  )      o  //                 (    o         _)
            OO(_    /--<  __, ,  // , , , __,  __  ,  `. ,  _ _ _    )
           oO (_   /   \_(_/(_(_(/_(_(_/_(_/(_/ (_/_(___)(_/ / / /   )
          O    (_                              __/                 _)
         Oo     (_                                                 )
        o         '=-___-===-_____-========-_______=___-===--==-='
      .o                                 
     . ______          ______________ ______________ ______________
   _()_||__|| ________ |            | |            | |            | 
  (         | |      | |  ________  | |  ________  | |  ________  | 
 /-OO----OO""="OO--OO"="OO--------OO"="OO--------OO"="OO--------OO"
#####################################################################
"""

import configparser
import copy
import ctypes
import os
import sys
import traceback
import warnings
import tempfile
import shutil

import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import qdarkstyle
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams
from matplotlib.pyplot import style
from matplotlib.ticker import AutoMinorLocator
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets as qtw
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QWidget
from termcolor import colored
from pathlib import Path

from . import integrated_csv_editor
from .resources import get_path
from .custom_mpl_toolbar import MyMplToolbar
from .ui.RailwaySim_GUI import Ui_MainWindow
from .ui.RailwaySim_GUI_pref import Ui_Form
from .save_restore import guisave
from .save_restore import guirestore
from .save_restore import grab_GC
from .data_formatter import get_text_positions
from .data_formatter import hhmm_to_s
from .data_formatter import text_plotter
from .data_formatter import effort_curve_to_arrays
from .solvers import ShortestOperationSolver

warnings.filterwarnings("ignore")

#? Use correct path for both bundled and dev versions
BASEDIR = get_path(Path(__file__).parent)

#* Dot separated values enforcement with "C"
QtCore.QLocale.setDefault(QtCore.QLocale(1))

#* Set icon on Windows taskbar
if sys.platform == 'win32':
    myappid = 'RailwaySim'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class NewWindow(QMainWindow):
    """MainWindow factory."""
    def __init__(self):
        super().__init__()
        GUI_preferences_path = str(Path.joinpath(BASEDIR, 'GUI_preferences.ini'))
        self.GUI_preferences = QtCore.QSettings(GUI_preferences_path, QtCore.QSettings.IniFormat)
        #* Allow multiple MainWindow instances
        self.window_list = []
        self.add_new_window()

    def add_new_window(self):
        """Creates new MainWindow instance."""
        self.app_icon = QIcon()
        app_icon_path = str(
            Path.joinpath(BASEDIR.parent, 'data', 'resources', 'images', 'RailwaySimIcon.png')
        )
        self.app_icon.addFile(app_icon_path)
        app.setWindowIcon(self.app_icon)
        window = MainWindow(self, self.GUI_preferences)
        window.setWindowIcon(self.app_icon)
        self.window_list.append(window)
        window.show()


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main application window."""
    def __init__(self, window, GUI):
        super().__init__()
        self.setupUi(self)
        self.windowManager = window
        self.GUI_preferences = GUI
        self.config = configparser.ConfigParser()
        self.config_is_set = 0  # Call tracker for config file
        self.simulation_finished = False
        self.instances_route_canvas = []
        self.instances_results_canvas = []
        self.instances_route_toolbar = []
        self.instances_results_toolbar = []
        self.statusBar().showMessage(str(BASEDIR))
        self._buttonEdits()
        self._mainEdits()

    def _iconFixes(self):
        '''Selects icon files for current stylesheet'''
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        if not self.dark_mode_set:
            darkPath = BASEDIR.parent / 'data' / 'resources' / 'images'
        else:
            darkPath = BASEDIR.parent / 'data' / 'resources' / 'images_dark'

        self.tabWidget.setTabIcon(
            self.tabWidget.indexOf(self.RollingStockTab),
            QtGui.QIcon(os.path.join(darkPath, 'rolling_tab.png'))
        )
        self.tabWidget.setTabIcon(
            self.tabWidget.indexOf(self.TractionChainTab),
            QtGui.QIcon(os.path.join(darkPath, 'traction_tab.png'))
        )
        self.tabWidget.setTabIcon(
            self.tabWidget.indexOf(self.RouteTab),
            QtGui.QIcon(os.path.join(darkPath, 'route_tab.png'))
        )
        self.tabWidget.setTabIcon(
            self.tabWidget.indexOf(self.SimulationTab),
            QtGui.QIcon(os.path.join(darkPath, 'sim_tab.png'))
        )
        self.actionSave.setIcon(QtGui.QIcon(os.path.join(darkPath, 'save.png')))
        self.actionOpen.setIcon(QtGui.QIcon(os.path.join(darkPath, 'open.png')))
        self.actionAbout.setIcon(QtGui.QIcon(os.path.join(darkPath, 'about.png')))
        self.actionEdit.setIcon(QtGui.QIcon(os.path.join(darkPath, 'settings.png')))
        self.actionExit.setIcon(QtGui.QIcon(os.path.join(darkPath, 'exit.png')))
        self.actionPrintToPDF.setIcon(QtGui.QIcon(os.path.join(darkPath, 'print.png')))
        self.actionSaveResults.setIcon(QtGui.QIcon(os.path.join(darkPath, 'download.png')))
        self.actionOpenResults.setVisible(False)  # Results will be associated to the .ini settings
        # self.actionOpenResults.setIcon(QtGui.QIcon(os.path.join(darkPath, 'upload.png')))
        self.actionNew_Window.setIcon(QtGui.QIcon(os.path.join(darkPath, 'new.png')))
        self.actionGitHub_Homepage.setIcon(QtGui.QIcon(os.path.join(darkPath, 'github.png')))
        icon_edit = QtGui.QIcon(os.path.join(darkPath, 'edit_csv.png'))
        icon_import = QtGui.QIcon(os.path.join(darkPath, 'import_csv.png'))
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
        #? "clicked" emits a signal (checked) when pressed:
        #? checkvoid QAbstractButton::clicked(bool checked = false)

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

        #* Draw route canvas after import
        self.ProfileLoadButton.clicked.connect(self.create_route_plot)
        self.ProfileLoadButton.clicked.connect(self.setup_route_checkbuttons)
        self.ProfileLoadButton.clicked.connect(self.dial_refresh)

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
        self.tabWidget.setCurrentIndex(0)  # Open on first tab by default

        #* Save results and report
        self.actionSaveResults.triggered.connect(self.save_results)

        #* PushButtons
        self.StartSimButton.clicked.connect(self.start_simulation)

        #* Toolbar buttons
        self.actionGitHub_Homepage.triggered.connect(self.GitHubLink)
        self.actionAbout.triggered.connect(self.AboutInfo)
        self.actionExit.triggered.connect(self.close)
        self.actionEdit.triggered.connect(self.show_preferences)

        #* Open and save triggers
        # WindowShortcut context is required with multiple windows
        self.actionNew_Window.triggered.connect(self.windowManager.add_new_window)
        self.actionOpen.triggered.connect(self.readFile)
        self.actionSave.triggered.connect(self.writeFile)
        self.actionSave_as.triggered.connect(self.writeNewFile)

        #* Instantiate and then restore theme preferences
        self.pref_screen = Preferences(self.GUI_preferences, self)
        self._iconFixes()  # change icons after Preferences are restored

        #* Spacer for empty Route and Simulation tab - must be defined as class var to allow removal
        self.spacerItem = qtw.QSpacerItem(
            20, 40, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Expanding
        )
        self.verticalLayout_2.addItem(self.spacerItem)
        self.verticalLayout_19.addItem(self.spacerItem)

        #* Loco or passenger train simulation selection
        self.gb_locomotive.toggled.connect(
            lambda checked: checked and self.gb_passenger.setChecked(False)
            if self.gb_passenger.isChecked() else checked
        )
        self.gb_passenger.toggled.connect(
            lambda checked: checked and self.gb_locomotive.setChecked(False)
            if self.gb_locomotive.isChecked() else checked
        )

        #* Dials
        self.dial_label_size.valueChanged.connect(self.dial_refresh)
        self.dial_stroke_size.valueChanged.connect(self.dial_refresh)
        self.dial_font_size.valueChanged.connect(self.dial_refresh)
        self.dial_label_size_results.valueChanged.connect(self.dial_refresh_results)
        self.dial_stroke_size_results.valueChanged.connect(self.dial_refresh_results)
        self.dial_font_size_results.valueChanged.connect(self.dial_refresh_results)

        #* System tray
        self.createTrayIcon()
        self.trayIcon.setIcon(self.windowManager.app_icon)
        self.trayIcon.messageClicked.connect(self.notification_handler)

        #* window exit
        qtw.QAction("Quit", self).triggered.connect(self.closeEvent)

    def save_results(self):
        """Saves the selected charts, simulation data and report into the chosen directory"""
        #TODO: this data will come from the temp folder (right after finishing the simulation)
        directory = qtw.QFileDialog.getExistingDirectory(
            self,
            "Select a directory to save results",
            str(BASEDIR),
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        print(directory)
        # os.makedirs(directory, exist_ok=True)

    def notification_handler(self):
        """Shows the results tab after the simulation is completed."""
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def changeEvent(self, event):
        """Hides the system tray icon when the main window is visible, and viceversa."""
        if event.type() == QtCore.QEvent.WindowStateChange and self.windowState(
        ) and self.isMinimized:
            self.trayIcon.show()
            event.accept()
        else:
            try:
                global message_is_being_shown
                if not message_is_being_shown:
                    self.trayIcon.hide()
            except:
                pass

    def dial_refresh(self):
        """Update route plot line width."""
        if len(self.ProfileLoadFilename.text()) > 3:
            self.linewidth = self.dial_stroke_size.value() / 2.5
            self.labelsize = 8 + self.dial_label_size.value()
            self.fontsize = 8 + self.dial_font_size.value()
            self.route_canvas.plot_route(self.linewidth, self.labelsize)
            self.route_canvas.fig.set_tight_layout(True)

    def dial_refresh_results(self):
        """Update route plot line width."""
        if self.simulation_finished:
            self.linewidth_results = self.dial_stroke_size_results.value() / 2.5
            self.labelsize_results = 8 + self.dial_label_size_results.value()
            self.fontsize_results = 8 + self.dial_font_size_results.value()
            self.results_canvas.plot_results(self.linewidth_results, self.labelsize_results)
            self.results_canvas.fig.set_tight_layout(True)

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
            try:
                if len(self.ProfileLoadFilename.text()) > 3:
                    self.route_canvas = PlotCanvas_route(self.GUI_preferences, self)
                    darkMode = bool(int(self.GUI_preferences.value('cb_dark')))
                    self.route_toolbar = MyMplToolbar(
                        self.route_canvas,
                        self.route_canvas,
                        coordinates=True,
                        darkMode=darkMode,
                        main_dir=str(BASEDIR.parent)
                    )
                    self.verticalLayout_2.addWidget(self.route_canvas)
                    self.verticalLayout_2.addWidget(self.route_toolbar)

                    #* Keep track of NavToolbar and Canvas
                    self.instances_route_canvas.append(self.route_canvas)
                    self.instances_route_toolbar.append(self.route_toolbar)
                    self.statusBar().showMessage(f"Loaded {self.ProfileLoadFilename.text()}.")
            except:
                pass

        else:
            self.statusBar().showMessage("Could not plot because no data was selected.")

    def create_results_plot(self):
        """Simulation results canvas and toolbar creator. 
        Called when a file is loaded and contains a results file path or after simulating."""
        if self.simulation_finished:
            #* Delete vertical spacer
            self.verticalLayout_19.removeItem(self.spacerItem)
            #* Delete previous instances if any
            try:
                self.instances_results_canvas[0].hide()
                self.instances_results_toolbar[0].hide()
                del self.instances_results_canvas[0]
                del self.instances_results_toolbar[0]
            except:
                pass
            #* Create new instances of canvas and toolbar
            if len(self.resultsFilename) > 3:
                self.results_canvas = PlotCanvas_results(self.GUI_preferences, self)
                darkMode = bool(int(self.GUI_preferences.value('cb_dark')))
                self.results_toolbar = MyMplToolbar(
                    self.results_canvas,
                    self.results_canvas,
                    coordinates=True,
                    darkMode=darkMode,
                    main_dir=str(BASEDIR.parent)
                )
                self.verticalLayout_19.addWidget(self.results_canvas)
                self.verticalLayout_19.addWidget(self.results_toolbar)

                #* Keep track of NavToolbar and Canvas
                self.instances_results_canvas.append(self.results_canvas)
                self.instances_results_toolbar.append(self.results_toolbar)
                self.statusBar().showMessage(f"Loaded results from {self.resultsFilename}.")

        else:
            self.statusBar(
            ).showMessage("Could not plot because no simulation has been carried out.")

    def setup_route_checkbuttons(self):
        """Route tab checkboxes. Must be called after each plot update."""
        if self.ProfileLoadFilename.text() == "":
            return
        try:
            if self.route_canvas is not None:
                self.route_checkbuttons = [
                    self.cb_r_stations,
                    self.cb_r_speedres,
                    self.cb_r_grade,
                    self.cb_r_profile,
                    self.cb_r_radii,
                    self.cb_r_legend,
                ]
                for cb in self.route_checkbuttons:
                    cb.stateChanged.connect(self.route_canvas.route_canvas_checkbox_handler)
                self.cb_InvertRoute.stateChanged.connect(
                    self.route_canvas.route_canvas_invert_route
                )
        except Exception as e:
            self.statusBar().showMessage("Could not setup checkboxes: " + str(e))

    def setup_results_checkbuttons(self):
        """Simulation tab checkboxes. Must be called after each plot update."""
        if not self.simulation_finished:
            return
        try:
            if self.results_canvas is not None:
                self.results_checkbuttons = [
                    self.cb_speedres_results,
                    self.cb_virtualspeedres_results,
                    self.cb_speed_results,
                    self.cb_grade_results,
                    self.cb_profile_results,
                    self.cb_radii_results,
                    self.cb_outputEffort_results,
                    self.cb_resistance_results,
                    self.cb_accel_results,
                    self.cb_stations_results,
                    self.cb_legend_results,
                ]
                for cb in self.results_checkbuttons:
                    cb.stateChanged.connect(self.results_canvas.results_canvas_checkbox_handler)
                #* Radiobuttons don't emit stateChanged
                self.radioButton_time.toggled.connect(
                    self.results_canvas.results_canvas_checkbox_handler
                )
                self.radioButton_distance.toggled.connect(
                    self.results_canvas.results_canvas_checkbox_handler
                )

        except Exception as e:
            self.statusBar().showMessage("Could not setup checkboxes: " + str(e))

    def createTrayIcon(self):
        self.restoreAction = qtw.QAction("&Restore", self, triggered=self.showNormal)
        self.quitAction = qtw.QAction("&Quit", self, triggered=qtw.QApplication.instance().quit)
        self.trayIconMenu = qtw.QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    #!#################   Methods out of init   ####################
    #!##############################################################

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
            str(BASEDIR),
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
            str(BASEDIR),
            'Configuration Files (*.ini)',
            options=qtw.QFileDialog.DontResolveSymlinks
        )
        self.resultsFilename = copy.deepcopy(self.filename).replace('.ini', '.csv')
        self.statusBar().showMessage(self.filename)
        if self.filename.lower().endswith('.ini'):
            try:
                self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
                # all values will be returned as QString
                guisave(self, self.my_settings)
                self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
                #* Save results to settings if the simulation was successful
                self.my_settings.setValue(
                    str('Results_file'), str(self.resultsFilename.replace('.ini', '.csv'))
                )
            except Exception as e:
                qtw.QMessageBox.critical(self, 'Error', f"Could not save settings: {e}")

    def readFile(self):  # ? Open
        """Restores GUI user input from a config file"""
        #* File dialog
        self.filename, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select a configuration file to load…",
            str(BASEDIR),
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
                    self.config.read(self.filename)
                    try:
                        self.resultsFilename = self.config['General']['Results_file']
                    except:
                        pass
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
                        self.dial_refresh()
                    #* Results WON'T be saved and plotted upon reopen
                    #* Additionally, clear canvas when opening any file
                    if self.simulation_finished:
                        try:
                            self.instances_results_canvas[0].hide()
                            self.instances_results_toolbar[0].hide()
                            del self.instances_results_canvas[0]
                            del self.instances_results_toolbar[0]
                        except:
                            pass
                except Exception as e:
                    qtw.QMessageBox.critical(self, 'Error', f"Could not open settings: {e}")
            else:
                qtw.QMessageBox.critical(
                    self, "Invalid file type", "Please select a .ini file.", qtw.QMessageBox.Ok
                )

    def writeFile(self):  # ? Save
        """Saves GUI user input to the previously opened config file"""
        if self.config_is_set and self.filename != "":
            self.statusBar().showMessage("Changes saved to: {}".format(self.filename))
            self.my_settings = QtCore.QSettings(self.filename, QtCore.QSettings.IniFormat)
            guisave(self, self.my_settings)
            self.resultsFilename = copy.deepcopy(self.filename).replace('.ini', '.csv')
            #* Save results to settings if the simulation was successful
            self.my_settings.setValue(
                str('Results_file'), str(self.resultsFilename.replace('.ini', '.csv'))
            )
        else:
            self.writeNewFile()

    def AboutInfo(self):
        """Shows license information"""
        self.infoScreen = qtw.QMessageBox(None)
        self.infoScreen.setWindowTitle('Legal Information')
        self.infoScreen.setText('RailwaySim is licenced under the GNU GPL v3.\t\t')
        self.infoScreen.setInformativeText("The complete license is available below.\t\t")
        try:
            self.infoScreen.setDetailedText(
                open(str(Path.joinpath(BASEDIR.parent.parent, "LICENSE")), "r",
                     encoding="utf-8").read()
            )
        except:
            self.infoScreen.setDetailedText("http://www.gnu.org/licenses/gpl-3.0.en.html")
        self.infoScreen.setWindowModality(QtCore.Qt.ApplicationModal)
        self.infoScreen.show()

    def GitHubLink(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://github.com/danicc097/RailwaySim'))

    def closeEvent(self, event):
        """Catches the MainWindow close button event and displays a dialog."""
        close = qtw.QMessageBox(qtw.QMessageBox.Question, 'Exit', 'Exit application?', parent=self)
        close_reject = close.addButton('No', qtw.QMessageBox.NoRole)
        close_accept = close.addButton('Yes', qtw.QMessageBox.AcceptRole)
        close.exec()  # Necessary for property-based API
        if close.clickedButton() == close_accept:
            self.trayIcon.setVisible(False)
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            event.accept()
        else:
            event.ignore()

    def showSuccess(self, sim_time):
        """System tray notification displaying simulation ended."""
        self.trayIcon.show()
        if not self.hasFocus():
            global message_is_being_shown
            message_is_being_shown = True
            self.trayIcon.showMessage(
                f"Simulation ended successfully in {sim_time} seconds!\n",
                "Click here to see the results.", self.windowManager.app_icon, 1200 * 1000
            )  # milliseconds default

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
            #* Save any changes to the GUI
            self.writeFile()
            #* Save current window's user input to a dict
            constants = grab_GC(self, self.my_settings)
            try:
                sim_time, self.stations_found = ShortestOperationSolver.main(
                    self, constants, self.resultsFilename
                )

                self.simulation_finished = True
                self.temp_dir = tempfile.mkdtemp()
                self.showSuccess(sim_time)
                #* Change current view to simulation tab and plot
                self.tabWidget.setCurrentIndex(3)
                #* Clear any old results
                try:
                    self.instances_results_canvas[0].hide()
                    self.instances_results_toolbar[0].hide()
                    del self.instances_results_canvas[0]
                    del self.instances_results_toolbar[0]
                except:
                    pass
                self.create_results_plot()
                self.setup_results_checkbuttons()
                self.dial_refresh_results()

                ################ Data for report #################
                #* Indexes must match after masking
                self.stations_found = self.stations_found.reset_index(drop=True)
                df_station_names = pd.DataFrame(
                    self.route_canvas.timetable_stations, columns=["Station"], dtype=str
                )
                self.stations_found.insert(1, "Station", df_station_names)
                self.sim_route_title = df_station_names.iloc[0].to_string(
                    header=False, index=False
                ) + " - " + df_station_names.iloc[-1].to_string(header=False, index=False)

                self.sim_route_length = str(
                    self.stations_found.iloc[-1]["KP [km]"].round(2)
                ) + " km"
                self.sim_route_max_grade = str(np.amax(self.route_canvas.grade, axis=0)) + " ‰"
                self.sim_route_min_grade = str(np.amin(self.route_canvas.grade, axis=0)) + " ‰"
                self.sim_route_avg_grade = str(
                    np.around(np.average(self.route_canvas.grade, axis=0), 3)
                ) + " ‰"
                t = str(self.stations_found.iloc[-1]["Elapsed time [hh:mm:ss]"]).split(':')
                t = [x.lstrip('0') for x in t]
                self.sim_route_time = f'{t[0]} hours, {t[1]} minutes and {t[2]} seconds.'
                #TODO: include traction plots, which were just plotted

                ##################################################

            except Exception as e:
                error_type, error, tb = sys.exc_info()
                print(colored((traceback.format_list(traceback.extract_tb(tb)[-1:])[-1]), "red"))
                print(colored(error_type, "yellow"))
                print(colored(error, "red"))


class PlotCanvas_route(FigureCanvas):
    """Route input data graph"""
    def __init__(self, GUI, ref_parent, dpi=100):
        self.GUI_preferences = GUI
        # Don't use "parent" as variable name.
        self.ref_parent = ref_parent  # pass MainWindow to access its widgets.
        self.fig = Figure(dpi=dpi)  # 100 dpi recommended
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.route_data_import(invert=self.ref_parent.cb_InvertRoute.isChecked())
        self.counter = 0  # Allow for plot retries upon exception

    def route_data_import(self, invert=False):
        """Route profile data import.\n
        Parameters
        ----------
        `invert`: flip route data (return trip). 
        """
        if len(self.ref_parent.ProfileLoadFilename.text()) <= 3:
            return

        # TODO: IF grouped route data by KP
        array = pd.DataFrame({'Time': [0, 10, 20, 25], 'Temperature': [50, 100, 120, 100]})
        array2 = pd.DataFrame({'Time': [0, 5, 10, 15], 'Height': [10, 11, 13, 15]})
        array3 = pd.DataFrame({'Time': [0, 20, 40], 'Width': [3, 5, 6]})
        concat_df = pd.concat([array, array2, array3])
        # concat_df.sort_values(by='Time', ascending=True, inplace=True)
        # concat_df = pd.concat([array,array2,array3]).groupby('Time')
        # print(concat_df)
        concat_df = concat_df.groupby('Time').sum(min_count=1)
        # print(concat_df)
        concat_df = concat_df.groupby('Time').sum(min_count=1).ffill()
        # print(concat_df)

        self.ROUTE_INPUT_DF = np.genfromtxt(
            self.ref_parent.ProfileLoadFilename.text(),
            delimiter=',',
            dtype=str,
            encoding='utf-8-sig',
            autostrip=True,
            deletechars="",
        )

        self.ROUTE_INPUT_DF = self.ROUTE_INPUT_DF[1:, :].T
        if invert:
            self.ROUTE_INPUT_DF = np.flip(self.ROUTE_INPUT_DF, axis=1)
        try:
            #* Minimum data to compute
            self.distance = np.array(self.ROUTE_INPUT_DF[3][:], dtype=float)
            self.kpoint = np.cumsum(self.distance / 1000, dtype=float)
            self.grade = np.array(self.ROUTE_INPUT_DF[4][:], dtype=float)
            self.radii = np.array(self.ROUTE_INPUT_DF[5][:], dtype=float)
            self.speed_res = np.array(self.ROUTE_INPUT_DF[6][:], dtype=float)

            #* Calculate profile height from distance steps and grade
            self.profile = np.zeros(len(self.distance), dtype=float)
            for index, distance_step in enumerate(self.distance):
                if index == 0:
                    self.profile[index] = 0
                else:
                    self.profile[
                        index] = distance_step * self.grade[index] / 1000 + \
                            self.profile[index-1]

            # * Main timetable
            self.timetable_stations = np.array(
                [str(a).strip() for a in self.ROUTE_INPUT_DF[0][:] if a != ""]
            )
            # * Find station kilometric points (0 m travelled paths)
            self.timetable_stations_kpoint = np.array(
                [self.kpoint[index] for index, a in enumerate(self.distance) if a == 0]
            )

            # * Optional timetables
            try:
                self.timetable_dwell_time = np.array(
                    [int(a) for a in self.ROUTE_INPUT_DF[1][:] if a != ""]
                )
            except:
                self.timetable_dwell_time = None
            try:
                self.timetable_arrival_time = np.array(
                    [hhmm_to_s(a) for a in self.ROUTE_INPUT_DF[2][:] if a != ""]
                )
            except:
                self.timetable_arrival_time = None

            self.plot_route(self.ref_parent.linewidth, self.ref_parent.labelsize)

        except:
            #* Attempt to replot once
            try:
                if self.counter == 0:
                    self.route_data_import(invert=self.cb_InvertRoute.isChecked())
                    self.counter += 1
            except:
                pass

    def plot_route(self, linewidth=2.5, labelsize=13):
        """Canvas and toolbar creation, deleting previous instances."""
        if len(self.ref_parent.instances_route_toolbar) > 1:
            self.ref_parent.instances_route_canvas[0].hide()
            self.ref_parent.instances_route_toolbar[0].hide()
            del self.ref_parent.instances_route_canvas[0]
            del self.ref_parent.instances_route_toolbar[0]

        self.fig.clear()  # clear wrong format if any on graph init

        #* Setting theme
        self.dark_mode_set = bool(int(self.GUI_preferences.value('cb_dark')))
        if self.dark_mode_set:
            self.fig.patch.set_facecolor(
                (0.09803921569, 0.13725490196, 0.17647058824)
            )  # light grey
            rcParams['axes.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)  # dark grey
            rcParams['text.color'] = rcParams['axes.labelcolor'] = rcParams[
                'axes.edgecolor'] = rcParams['xtick.color'] = rcParams['ytick.color'] = 'white'
            rcParams['savefig.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)
        else:
            style.use('default')
            self.fig.patch.set_facecolor('white')
        rcParams['savefig.dpi'] = 300
        path = str(
            Path.joinpath(
                BASEDIR.parent, 'data', 'resources', 'fonts', 'Fira_Sans', 'FiraSans-Medium.ttf'
            )
        )
        prop = font_manager.FontProperties(fname=path)
        # font_manager._rebuild()
        rcParams['font.family'] = prop.get_name()
        rcParams['font.weight'] = 'regular'
        rcParams["axes.labelweight"] = 'regular'
        rcParams['font.size'] = self.ref_parent.fontsize
        rcParams["axes.labelsize"] = self.ref_parent.fontsize

        #* Plot axes
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Distance [km]")
        self.ax.set_ylabel("Speed [km/h]", )
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())

        try:
            #* Plotting on main axis sharing X
            if self.ref_parent.cb_r_speedres.isChecked():
                self.line0, = self.ax.step(
                    self.kpoint,
                    self.speed_res,
                    linewidth=linewidth,
                    label="Speed [km/h]",
                    where="pre"
                )

            if self.ref_parent.cb_r_grade.isChecked():
                self.line1, = self.ax.step(
                    self.kpoint, self.grade, linewidth=linewidth, label="Grade [‰]", where="pre"
                )

            if self.ref_parent.cb_r_profile.isChecked():
                self.line3, = self.ax.plot(
                    self.kpoint, self.profile, linewidth=linewidth, label="Profile [m]"
                )

            #* Twin axis Y - station tick marks
            if self.ref_parent.cb_r_stations.isChecked():
                self.ax2 = self.ax.twiny()
                self.ax2.set_xlim(self.ax.get_xlim())
                self.ax2.set_label('Stations')
                #* optionally add vertical lines at each of the station positions
                for x in self.timetable_stations_kpoint:
                    self.ax2.axvline(x, color='red', alpha=0.5, ls=':', lw=1.5)

                # ? Offset tick labels alternative
                txt_height = max(self.ax.get_ylim()) / (8.5)
                txt_width = max(self.ax.get_xlim()) / (110)
                # + 0.005 * labelsize
                # # Get the corrected text positions, then write the text.
                y_height = [max(self.ax.get_ylim())] * len(self.timetable_stations_kpoint)
                text_positions = get_text_positions(
                    self.timetable_stations_kpoint,
                    y_height,
                    txt_width,
                    txt_height,
                )
                text_plotter(
                    self.timetable_stations_kpoint, self.timetable_stations, y_height,
                    text_positions, self.ax, txt_width, txt_height, labelsize, self.dark_mode_set
                )
                self.ax2.xaxis.set_minor_locator(ticker.NullLocator())
                self.ax2.xaxis.set_major_locator(ticker.NullLocator())

            plt.xticks([])  # remove secondary ticks

            #* Twin axis X - Radii
            if self.ref_parent.cb_r_radii.isChecked():
                self.ax3 = self.ax.twinx()
                self.ax3.set_label('Distance [km] - Radii [m]')
                self.ax3.set_ylabel('Radii [m]')
                self.ax3.set_ylim(top=np.amax(self.radii) * 4, bottom=0)
                self.line2, = self.ax3.step(
                    self.kpoint,
                    self.radii,
                    linewidth=self.ref_parent.linewidth,
                    label="Radii [m]",
                    where="pre"
                )
                self.line2.set_color("purple")

            #* Line color has to be set during/after axis plot
            if self.dark_mode_set:
                try:
                    self.line0.set_color("white")
                    self.line1.set_color("orange")
                    self.line2.set_color("cyan")
                    self.line3.set_color("lime")
                except:
                    pass

            #* Include watermark if any
            global watermark
            self.fig.text(
                0.5,
                0.5,
                watermark,
                fontsize=20,
                color='gray',
                ha='center',
                va='center',
                alpha=0.6,
                transform=self.ax.transAxes
            )

            #* Chart legend
            if self.ref_parent.cb_r_legend.isChecked():
                handles, labels = [], []
                for ax in self.fig.axes:
                    for h, l in zip(*ax.get_legend_handles_labels()):
                        handles.append(h)
                        labels.append(l)
                self.ax.legend(handles, labels)

            self.fig.tight_layout()
            self.draw()
        except AttributeError:
            qtw.QMessageBox.critical(self, "Error", "Not a valid route format.")

    def route_canvas_checkbox_handler(self):
        """Replot on checkbox state change."""
        try:
            self.plot_route(self.ref_parent.linewidth, self.ref_parent.labelsize)
        except:
            pass

    def route_canvas_invert_route(self):
        """Replot on checkbox state change."""
        try:
            self.route_data_import(invert=self.ref_parent.cb_InvertRoute.isChecked())
            self.plot_route(self.ref_parent.linewidth, self.ref_parent.labelsize)
        except:
            pass


class PlotCanvas_results(FigureCanvas):
    """Simulation output data graph"""
    def __init__(self, GUI, ref_parent, dpi=100):
        self.GUI_preferences = GUI
        # Don't use "parent" as variable name
        self.ref_parent = ref_parent  # pass MainWindow to access its widgets
        self.fig = Figure(dpi=dpi)  # 100 dpi recommended
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.df = pd.read_csv(self.ref_parent.resultsFilename)

    def plot_results(self, linewidth=2.5, labelsize=13):
        """Canvas and toolbar creation, deleting previous instances."""
        if len(self.ref_parent.instances_results_toolbar) > 1:
            self.ref_parent.instances_results_canvas[0].hide()
            self.ref_parent.instances_results_toolbar[0].hide()
            del self.ref_parent.instances_results_canvas[0]
            del self.ref_parent.instances_results_toolbar[0]

        self.fig.clear()  # clear wrong format if any on graph init

        #* No dark mode to create the report properly
        self.dark_mode_set = False
        if self.dark_mode_set:
            self.fig.patch.set_facecolor(
                (0.09803921569, 0.13725490196, 0.17647058824)
            )  # light grey
            rcParams['axes.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)  # dark grey
            rcParams['text.color'] = rcParams['axes.labelcolor'] = rcParams[
                'axes.edgecolor'] = rcParams['xtick.color'] = rcParams['ytick.color'] = 'white'
            rcParams['savefig.facecolor'] = (0.19607843137, 0.25490196078, 0.29411764706)
        else:
            style.use('default')
            self.fig.patch.set_facecolor('white')
        rcParams['savefig.dpi'] = 300
        path = str(
            Path.joinpath(
                BASEDIR.parent, 'data', 'resources', 'fonts', 'Fira_Sans', 'FiraSans-Medium.ttf'
            )
        )
        prop = font_manager.FontProperties(fname=path)
        # font_manager._rebuild()
        rcParams['font.family'] = prop.get_name()
        rcParams['font.weight'] = 'regular'
        rcParams["axes.labelweight"] = 'regular'
        rcParams['font.size'] = self.ref_parent.fontsize_results
        rcParams["axes.labelsize"] = self.ref_parent.fontsize_results

        #* Plot axes
        self.ax = self.fig.add_subplot(111)
        if self.ref_parent.radioButton_distance.isChecked():
            self.ax.set_xlabel("Distance [km]")
            x_axis = self.df['KP [km]']
        else:
            self.ax.set_xlabel("Time [s]")
            x_axis = self.df['Elapsed time [s]']

        self.ax.set_ylabel("Speed [km/h]")
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())

        #* Plotting on main axis sharing X
        if self.ref_parent.cb_speedres_results.isChecked():
            self.line0, = self.ax.step(
                x_axis,
                self.df['Speed restriction [km/h]'],  #*ROUTE DATA
                linewidth=linewidth,
                label="Speed restriction [km/h]",
                where="pre"
            )

        if self.ref_parent.cb_virtualspeedres_results.isChecked():
            self.line1, = self.ax.step(
                x_axis,
                self.df['Virtual speed restriction [km/h]'],
                linewidth=linewidth,
                label="Virtual speed restriction [km/h]",
                where="pre"
            )
        if self.ref_parent.cb_speed_results.isChecked():
            self.line2, = self.ax.plot(
                x_axis,
                self.df['Speed [km/h]'],
                linewidth=linewidth,
                label="Speed [km/h]",
            )
        if self.ref_parent.cb_grade_results.isChecked():
            self.line3, = self.ax.step(
                x_axis, self.df['Grade [‰]'], linewidth=linewidth, label="Grade [‰]", where="pre"
            )

        if self.ref_parent.cb_profile_results.isChecked():
            self.line4, = self.ax.plot(
                x_axis, self.df['Profile [m]'], linewidth=linewidth, label="Profile [m]"
            )
        if self.ref_parent.cb_resistance_results.isChecked():
            self.line5, = self.ax.plot(
                x_axis, self.df['Resistance [kN]'], linewidth=linewidth, label="Resistance [kN]"
            )
        if self.ref_parent.cb_accel_results.isChecked():
            self.line6, = self.ax.plot(
                x_axis,
                self.df['Acceleration [m/s²]'],
                linewidth=linewidth,
                label="Acceleration [m/s²]"
            )
        self.df['Braking Effort [kN]'] = -abs(self.df['Braking Effort [kN]'])
        self.outputEffort = self.df[['Tractive Effort [kN]', 'Braking Effort [kN]']].sum(axis=1)
        if self.ref_parent.cb_outputEffort_results.isChecked():
            self.line7, = self.ax.plot(
                x_axis, self.outputEffort, linewidth=linewidth, label="Effort [kN]"
            )

        # TODO stations in results tab
        # #* Twin axis Y - station tick marks
        # if self.ref_parent.cb_stations_results.isChecked():
        #     self.ax2 = self.ax.twiny()
        #     self.ax2.set_xlim(self.ax.get_xlim())
        #     self.ax2.set_label('Stations')
        #     #* optionally add vertical lines at each of the station positions
        #     for x in self.timetable_stations_kpoint:
        #         self.ax2.axvline(x, color='red', alpha=0.5, ls=':', lw=1.5)

        #     # ? Offset tick labels alternative
        #     txt_height = max(self.ax.get_ylim()) / (8.5)
        #     txt_width = max(self.ax.get_xlim()) / (110)
        #     # + 0.005 * labelsize
        #     # # Get the corrected text positions, then write the text.
        #     y_height = [max(self.ax.get_ylim())] * len(self.timetable_stations_kpoint)
        #     text_positions = get_text_positions(
        #         self.timetable_stations_kpoint,
        #         y_height,
        #         txt_width,
        #         txt_height,
        #     )
        #     text_plotter(
        #         self.timetable_stations_kpoint, self.timetable_stations, y_height, text_positions,
        #         self.ax, txt_width, txt_height, labelsize, self.dark_mode_set
        #     )
        #     self.ax2.xaxis.set_minor_locator(ticker.NullLocator())
        #     self.ax2.xaxis.set_major_locator(ticker.NullLocator())

        plt.xticks([])  # remove secondary ticks

        #* Twin axis X - Radii
        if self.ref_parent.cb_radii_results.isChecked():
            self.ax3 = self.ax.twinx()
            if self.ref_parent.radioButton_distance.isChecked():
                self.ax3.set_label('Distance [km] - Radii [m]')
            else:
                self.ax3.set_label('Time [s] - Radii [m]')
            self.ax3.set_ylabel('Radii [m]')
            self.ax3.set_ylim(top=np.amax(self.df['Radius [m]']) * 4, bottom=0)
            self.line5, = self.ax3.step(
                x_axis,
                self.df['Radius [m]'],
                linewidth=self.ref_parent.linewidth_results,
                label="Radius [m]",
                where="pre"
            )
            self.line2.set_color("purple")

        #* Line color has to be set during/after axis plot
        if self.dark_mode_set: self.line0.set_color("white")

        #* Include watermark if any
        global watermark
        self.fig.text(
            0.5,
            0.5,
            watermark,
            fontsize=20,
            color='gray',
            ha='center',
            va='center',
            alpha=0.6,
            transform=self.ax.transAxes
        )

        #* Chart legend
        if self.ref_parent.cb_legend_results.isChecked():
            handles, labels = [], []
            for ax in self.fig.axes:
                for h, l in zip(*ax.get_legend_handles_labels()):
                    handles.append(h)
                    labels.append(l)
            self.ax.legend(handles, labels)

        self.fig.tight_layout()
        self.draw()

        #TODO: plot and save traction curves by default to folder
        self.plot_save_traction_curve()

    def plot_save_traction_curve(self):
        fig_traction, ax = plt.subplots()
        ax.set_xlabel("Speed [km/h]")
        ax.set_ylabel("Effort [kN]")

        if self.ref_parent.gb_electric_traction.isChecked():
            Electric_T_speed, Electric_T_effort = effort_curve_to_arrays(
                self.ref_parent.E_TECurveLoadFilename.text()
            )
            Electric_B_speed, Electric_B_effort = effort_curve_to_arrays(
                self.ref_parent.E_BECurveLoadFilename.text()
            )
            line0, = ax.plot(
                Electric_T_speed,
                Electric_T_effort,
                label="Electric effort [kN]",
            )
        if self.ref_parent.gb_diesel_engine.isChecked():
            Diesel_T_speed, Diesel_T_effort = effort_curve_to_arrays(
                self.ref_parent.D_TECurveLoadFilename.text()
            )
            Diesel_B_speed, Diesel_B_effort = effort_curve_to_arrays(
                self.ref_parent.D_BECurveLoadFilename.text()
            )
            line1, = ax.plot(
                Diesel_T_speed,
                Diesel_T_effort,
                label="Diesel effort [kN]",
            )

        global watermark
        fig_traction.text(
            0.5,
            0.5,
            watermark,
            fontsize=20,
            color='gray',
            ha='center',
            va='center',
            alpha=0.6,
            transform=ax.transAxes
        )
        handles, labels = [], []
        for ax in fig_traction.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                handles.append(h)
                labels.append(l)
        ax.legend(handles, labels)

        #* Save traction curves to a temp folder
        rcParams["savefig.format"] = 'svg'
        fig_path = os.path.join(self.ref_parent.temp_dir, "traction_curves.svg")
        fig_traction.savefig(fig_path)

    def results_canvas_checkbox_handler(self):
        """Replot on checkbox state change."""
        try:
            self.plot_results(self.ref_parent.linewidth_results, self.ref_parent.labelsize_results)
        except:
            pass


class Preferences(QWidget, Ui_Form):
    """Preferences widget screen. Initialized alongside window."""
    def __init__(self, GUI, ref_parent=None):
        super().__init__()
        self.setupUi(self)

        #* Optional param to access attributes
        self.ref_parent = ref_parent

        #* Restore latest .ini GUI config
        self.GUI_preferences = GUI
        try:
            guirestore(self, self.GUI_preferences)
        except:  # Create new empty file if none found
            guisave(self, self.GUI_preferences)

        global watermark
        watermark = ""

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
                app.setStyleSheet('')  # Default style
            else:
                app.setStyleSheet(qdarkstyle.load_stylesheet())

            # * Update icons
            for window in self.ref_parent.windowManager.window_list:
                window._iconFixes()

            # * Update plot
            self.window_plot_update()

        except:
            pass

    def cb_watermark_check(self):
        """Define watermark based on checkbox state and line text"""
        global watermark
        watermark = self.watermark.text() if self.cb_watermark.isChecked() else ""
        #* Redraw canvas application-wide
        for window in self.ref_parent.windowManager.window_list:
            try:
                window.route_canvas.plot_route(self.ref_parent.linewidth, self.ref_parent.labelsize)
                window.results_canvas.plot_results(
                    self.ref_parent.linewidth_results, self.ref_parent.labelsize_results
                )
            except:
                pass
        guisave(self, self.GUI_preferences)

    def window_plot_update(self):
        """Update icons and replot in all windows"""
        for _, window in enumerate(self.ref_parent.windowManager.window_list):
            window._iconFixes()
            window.route_canvas = PlotCanvas_route(window.GUI_preferences, window)
            darkMode = bool(int(window.GUI_preferences.value('cb_dark')))
            window.route_toolbar = MyMplToolbar(
                window.route_canvas,
                window.route_canvas,
                coordinates=True,
                darkMode=darkMode,
                main_dir=str(BASEDIR.parent)
            )

            window.verticalLayout_2.addWidget(window.route_canvas)
            window.verticalLayout_2.addWidget(window.route_toolbar)
            window.instances_route_canvas.append(window.route_canvas)
            window.instances_route_toolbar.append(window.route_toolbar)

            #* Keep only one route canvas and toolbar in memory
            #* Delete blank charts where no file was selected (len == 1)
            if len(window.instances_route_toolbar) > 0:
                window.instances_route_canvas[0].hide()
                window.instances_route_toolbar[0].hide()
                del window.instances_route_canvas[0]
                del window.instances_route_toolbar[0]

            #* Results tab doesn't use dark mode, i.e. no logic for it
            #* Except for its toolbar
            window.instances_results_toolbar[0].hide()
            del window.instances_results_toolbar[0]
            window.results_toolbar = MyMplToolbar(
                window.results_canvas,
                window.results_canvas,
                coordinates=True,
                darkMode=darkMode,
                main_dir=str(BASEDIR.parent)
            )
            window.verticalLayout_19.addWidget(window.results_toolbar)
            window.instances_results_toolbar.append(window.results_toolbar)

    def hide_preferences(self):
        """Exits Preferences window"""
        self.cb_watermark_check()
        try:
            for window in self.ref_parent.windowManager.window_list:
                window.setup_route_checkbuttons()  # Must be called every replot
                window.setup_results_checkbuttons()  # Must be called every replot
        except:
            pass
        self.hide()


# if __name__ == "__main__":
app = qtw.QApplication(sys.argv)
app.setStyle('Fusion')  # ['windowsvista', 'Windows', 'Fusion']
app.setApplicationName('RailwaySim')
app.setApplicationVersion('1.0')
path = Path.joinpath(
    BASEDIR.parent, 'data', 'resources', 'fonts', 'Fira_Sans', 'FiraSans-Medium.ttf'
)
id = QtGui.QFontDatabase.addApplicationFont(str(path))
family = QtGui.QFontDatabase.applicationFontFamilies(id)[0]
font = QtGui.QFont(family, 9)
app.setFont(font)

w = NewWindow()  # Instantiate window factory

#* Exit with Ctrl + C
timer = QtCore.QTimer()
timer.timeout.connect(lambda: None)
timer.start(100)
sys.exit(app.exec_())
"""
# * ImageMagick icons: magick mogrify tranparent -channel RGB -negate *.png
"""
