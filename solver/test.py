# import numpy as np

# ini_array = np.array([['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']])

# print("initial_array : ", ini_array)

# # Array to be added as column
# column_to_be_added = np.array([1, 2, 3])

# # Adding column to numpy array
# result = np.hstack((ini_array, np.atleast_2d(column_to_be_added).T))

# # Adding row to numpy array
# result2 = np.stack((ini_array, (column_to_be_added).T))

# print("resultant array hstack", result)
# print("resultant array vstack", result2)

# def namelist(names):
#     output = ""

#     for i in range(len(names)):
#         if i == 0:
#             output += names[i]['name']
#         elif i == len(names) - 1:
#             output += " & " + names[i]['name']
#         else:
#             output += ", " + names[i]['name']

#     return output

# namelist1 = [{'name': 'Bart'}, {'name': 'Lisa'}, {'name': 'Maggie'}]
# print(namelist(namelist1))

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize
import pandas as pd
import sys


class MainFrame(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        data = [
            ["A", "00:00:01", True, 0], ["B", "00:00:05", False, 1], ["C", "00:00:07", False, 2],
            ["D", "00:00:08", False, 3], ["E", "00:00:13", False, 2], ["F", "00:00:17", False, 1],
            ["G", "00:00:21", True, 0]
        ]

        self.event_table = QtWidgets.QTableView()
        self.event_table.horizontalHeader().setStretchLastSection(True)
        df = pd.DataFrame(data, columns=["Event", "Time", "root", "Deepness"])
        self.model = EventTableModel(df)
        self.event_table.setModel(self.model)
        self.setCentralWidget(self.event_table)
        self.event_table.resizeRowsToContents()
        self.resize(800, 600)


class EventTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(EventTableModel, self).__init__()
        self._data = data
        self._color = QtGui.QBrush(QtGui.QColor(230, 230, 230))

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        if role == QtCore.Qt.BackgroundRole and index.row() % 2 == 0:
            #return QtGui.QBrush(QtGui.QColor(230, 230, 230))
            return self._color

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainFrame()
    main.show()
    sys.exit(app.exec_())