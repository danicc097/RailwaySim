# https://matplotlib.org/gallery/user_interfaces/embedding_in_qt_sgskip.html

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
# Transpose to generate column by column
dataset_np = dataset_np.T

# mask = np.all(dataset_np == "", axis=1)
# dataset_np = dataset_np[~mask]
# print('dataset_np')
# print(dataset_np)
# print('dataset_np[0][0]')
# print(dataset_np[0][0])
# print('dataset_np[0][1]')
# print(dataset_np[0][1])
# print('dataset_np[0]')
# print(dataset_np[0])
# print('dataset_np[1]')
# print(dataset_np[1])


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
        x_axis1 = [float(a) for a in dataset_np[8][1:] if a != ""]  # Removes empty last row
        y_axis1 = [float(a) for a in dataset_np[9][1:] if a != ""]
        x_axis2 = [float(a) for a in dataset_np[0][1:] if a != ""]
        y_axis2 = [str(a) for a in dataset_np[1][1:] if a != ""]
        x_axis3 = [float(a) for a in dataset_np[4][1:] if a != ""]
        y_axis3 = [float(a) for a in dataset_np[5][1:] if a != ""]

        self.ax.set_xlabel("Distance [km]")
        self.ax.set_ylabel("Speed [km/h]")
        self.l0, = self.ax.step(x_axis1, y_axis1, label="Speed", where="post")
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
            rotation=60
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
        self.ax3.step(x_axis3, y_axis3, color="green")
        self.ax3.tick_params(axis='y', labelcolor="black")

        # * CheckButtons
        self.lines = [self.l0, self.ax2, self.ax3]
        self.rax = self.static_canvas.figure.add_axes([0, 0, 0.12, 0.1])  # ! Change this, probably
        self.labels = [str(line.get_label()) for line in self.lines]
        self.visibility = [line.get_visible() for line in self.lines]
        self.check = CheckButtons(self.rax, self.labels, self.visibility)
        self.check.on_clicked(self.on_clicked)

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