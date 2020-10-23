# https://matplotlib.org/gallery/user_interfaces/embedding_in_qt_sgskip.html
# https://stackoverflow.com/questions/46816400/matplotlib-checkbuttons-in-a-row

import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar
    )
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar
    )
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib import rcParams
from matplotlib.ticker import FixedLocator, FixedFormatter
#rcParams['font.family'] = 'Euclid'
rcParams.update({'font.size': 12})

with open('RailwaySim/Input_template.csv', mode='r', encoding='utf-8-sig') as f:
    dataset_np = np.genfromtxt(
        'RailwaySim/Input_template.csv',
        delimiter=',',
        dtype=float and str,
        encoding='utf-8-sig',
        autostrip=True,
        deletechars=""
    )
# Transpose to store csv column by column
dataset_np = dataset_np.T

# mask = np.all(dataset_np == "", axis=1)
# dataset_np = dataset_np[~mask]


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        self.static_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.static_canvas)
        self.addToolBar(NavigationToolbar(self.static_canvas, self))

        self.ax = self.static_canvas.figure.subplots()

        # ! MAIN DATA
        # listcomp removes empty last row
        x_axis1 = [float(a) for a in dataset_np[8][1:] if a != ""]  # Speed limitation
        y_axis1 = [float(a) for a in dataset_np[9][1:] if a != ""]
        x_axis2 = [float(a) for a in dataset_np[0][1:] if a != ""]  # Stations
        y_axis2 = [str(a) for a in dataset_np[1][1:] if a != ""]
        x_axis3 = [float(a) for a in dataset_np[4][1:] if a != ""]  # Grade
        y_axis3 = [float(a) for a in dataset_np[5][1:] if a != ""]
        x_axis4 = [float(a) for a in dataset_np[6][1:] if a != ""]  # Radius
        y_axis4 = [float(a) for a in dataset_np[7][1:] if a != ""]

        self.ax.set_xlabel("Distance [km]")
        self.ax.set_ylabel("Speed [km/h]")
        self.ax.grid(b=True, which="major", axis="both")
        self.ax.tick_params(
            direction="in",
            length=7,
        )
        self.mainLine, = self.ax.step(x_axis1, y_axis1, label="Speed", where="post")
        self.ax2 = self.ax.twiny()
        self.ax2.set_xlim(self.ax.get_xlim())
        self.ax2.set_label('Stations')
        self.ax2.tick_params(
            axis="x",
            which='major',
            direction="in",
            width=1.5,
            length=7,
            labelsize=12,
            color="red",
            rotation=50
        )
        x_locator = FixedLocator(x_axis2)
        x_formatter = FixedFormatter(y_axis2)
        self.ax2.xaxis.set_major_locator(
            x_locator
        )  # it's best to first set the locator and only then the formatter
        self.ax2.xaxis.set_major_formatter(x_formatter)
        # ? optionally add vertical lines at each of the station positions
        for x in x_axis2:
            self.ax2.axvline(x, color='red', ls=':', lw=1.5)

        self.ax3 = self.ax.twinx()
        self.ax3.set_label('Grade [‰]')
        self.ax3.set_ylabel('Grade [‰]', color="black")  # we already handled the x-label with ax
        self.ax3.step(x_axis3, y_axis3, color="green", where="post")
        self.ax3.tick_params(
            axis='y',
            labelcolor="black",
            direction="in",
        )

        self.ax4 = self.ax.twinx()
        self.ax4.set_label('Radius [m]')
        self.ax4.set_ylabel('Radius [m]', color="black")  # we already handled the x-label with ax
        self.ax4.step(x_axis4, y_axis4, color="darkviolet", where="post")
        self.ax4.tick_params(
            axis='y',
            labelcolor="black",
            direction="in",
        )

        # * CheckButtons
        self.lines = [self.mainLine, self.ax2, self.ax3, self.ax4]
        self.rax = self.static_canvas.figure.add_axes(
            [0, 0, 0.15, 0.1],
            frameon=True,
        )  # ! Change this dynamically and hide to print
        self.labels = [str(line.get_label()) for line in self.lines]
        self.visibility = [line.get_visible() for line in self.lines]
        self.check = CheckButtons(self.rax, self.labels, self.visibility)
        self.check.on_clicked(self.on_clicked)
        for r in self.check.rectangles:
            r.set_facecolor("blue")
            r.set_edgecolor("k")
            r.set_alpha(0.2)
        [ll.set_color("blue") for l in self.check.lines for ll in l]
        [ll.set_linewidth(1) for l in self.check.lines for ll in l]
        self.static_canvas.figure.tight_layout()

    def on_clicked(self, label):
        self.index = self.labels.index(label)
        self.lines[self.index].set_visible(not self.lines[self.index].get_visible())
        self.static_canvas.draw()


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()