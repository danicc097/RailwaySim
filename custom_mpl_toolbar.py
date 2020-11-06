import functools
import os
import re
import signal
import sys
import traceback

import matplotlib

from matplotlib import backend_tools, cbook
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import (
    _Backend, FigureCanvasBase, FigureManagerBase, NavigationToolbar2, TimerBase, cursors,
    ToolContainerBase, StatusbarBase, MouseButton
)
import matplotlib.backends.qt_editor.figureoptions as figureoptions
from matplotlib.backends.qt_editor.formsubplottool import UiSubplotTool
from matplotlib.backend_managers import ToolManager

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import cursors as mplCursors
from matplotlib.figure import Figure
import os
import PyQt5.QtGui as QtGui
import matplotlib

from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import (
    _Backend, FigureCanvasBase, FigureManagerBase, NavigationToolbar2, TimerBase, cursors,
    ToolContainerBase, StatusbarBase, MouseButton
)

from matplotlib.backends.qt_compat import (
    QtCore, QtGui, QtWidgets, _getSaveFileName, is_pyqt5, __version__, QT_API
)

BASEDIR = os.path.dirname(__file__)
# define which modifier keys are collected on keyboard events.
# elements are (mpl names, Modifier Flag, Qt Key) tuples
SUPER = 0
ALT = 1
CTRL = 2
SHIFT = 3
MODIFIER_KEYS = [
    ('super', QtCore.Qt.MetaModifier, QtCore.Qt.Key_Meta),
    ('alt', QtCore.Qt.AltModifier, QtCore.Qt.Key_Alt),
    ('ctrl', QtCore.Qt.ControlModifier, QtCore.Qt.Key_Control),
    ('shift', QtCore.Qt.ShiftModifier, QtCore.Qt.Key_Shift),
]

cursord = {
    cursors.MOVE: QtCore.Qt.SizeAllCursor,
    cursors.HAND: QtCore.Qt.PointingHandCursor,
    cursors.POINTER: QtCore.Qt.ArrowCursor,
    cursors.SELECT_REGION: QtCore.Qt.CrossCursor,
    cursors.WAIT: QtCore.Qt.WaitCursor,
}


class MyMplToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, coordinates=True, darkMode=True):
        self.canvas = canvas
        self.parent = parent
        self.coordinates = coordinates
        self._actions = {}
        self.darkMode = darkMode
        QtWidgets.QToolBar.__init__(self, parent)
        NavigationToolbar2.__init__(self, canvas)

    def _init_toolbar(self):
        # ! Choose icon theme
        if self.darkMode == True:
            self.basedir = os.path.join(BASEDIR, 'resources/images_dark/matplotlib-dark-images')
        else:
            self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'), text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)
                if text == 'Subplots':
                    a = self.addAction(
                        self._icon("qt4_editor_options.png"), 'Customize', self.edit_parameters
                    )
                    a.setToolTip('Edit axis, curve and image parameters')

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.locLabel.setSizePolicy(
                QtWidgets.QSizePolicy(
                    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored
                )
            )
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # Esthetic adjustments - we need to set these explicitly in PyQt5
        # otherwise the layout looks different - but we don't want to set it if
        # not using HiDPI icons otherwise they look worse than before.
        if is_pyqt5() and self.canvas._dpi_ratio > 1:
            self.setIconSize(QtCore.QSize(24, 24))
            self.layout().setSpacing(12)

    @cbook.deprecated("3.1")
    @property
    def buttons(self):
        return {}

    @cbook.deprecated("3.1")
    @property
    def adj_window(self):
        return None

    def sizeHint(self):
        size = super().sizeHint()
        if is_pyqt5() and self.canvas._dpi_ratio > 1:
            # For some reason, self.setMinimumHeight doesn't seem to carry over
            # to the actual sizeHint, so override it instead in order to make
            # the aesthetic adjustments noted above.
            size.setHeight(max(48, size.height()))
        return size

    def edit_parameters(self):
        axes = self.canvas.figure.get_axes()
        if not axes:
            QtWidgets.QMessageBox.warning(self.parent, "Error", "There are no axes to edit.")
            return
        elif len(axes) == 1:
            ax, = axes
        else:
            titles = [
                ax.get_label() or ax.get_title()
                or " - ".join(filter(None, [ax.get_xlabel(), ax.get_ylabel()]))
                or f"<anonymous {type(ax).__name__}>" for ax in axes
            ]
            duplicate_titles = [title for title in titles if titles.count(title) > 1]
            for i, ax in enumerate(axes):
                if titles[i] in duplicate_titles:
                    titles[i] += f" (id: {id(ax):#x})"  # Deduplicate titles.
            item, ok = QtWidgets.QInputDialog.getItem(
                self.parent, 'Customize', 'Select axes:', titles, 0, False
            )
            if not ok:
                return
            ax = axes[titles.index(item)]
        figureoptions.figure_edit(ax, self)

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['zoom'].setChecked(self._active == 'ZOOM')

    def pan(self, *args):
        super().pan(*args)
        self._update_buttons_checked()

    def zoom(self, *args):
        super().zoom(*args)
        self._update_buttons_checked()

    def set_message(self, s):
        self.message.emit(s)
        if self.coordinates:
            self.locLabel.setText(s)

    def set_cursor(self, cursor):
        self.canvas.setCursor(cursord[cursor])

    def draw_rubberband(self, event, x0, y0, x1, y1):
        height = self.canvas.figure.bbox.height
        y1 = height - y1
        y0 = height - y0
        rect = [int(val) for val in (x0, y0, x1 - x0, y1 - y0)]
        self.canvas.drawRectangle(rect)

    def remove_rubberband(self):
        self.canvas.drawRectangle(None)

    def configure_subplots(self):
        image = os.path.join(matplotlib.rcParams['datapath'], 'images', 'matplotlib.png')
        dia = SubplotToolQt(
            self.canvas.figure, self.canvas.figure
        )  #! , self.canvas.figure <-- , self.canvas.parent()
        dia.setWindowIcon(QtGui.QIcon(image))
        dia.exec_()

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = sorted(filetypes.items())
        default_filetype = self.canvas.get_default_filetype()

        startpath = os.path.expanduser(matplotlib.rcParams['savefig.directory'])
        start = os.path.join(startpath, self.canvas.get_default_filename())
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)

        fname, filter = _getSaveFileName(
            None,  #! None - self.canvas.parent()
            "Choose a filename to save to",
            start,
            filters,
            selectedFilter
        )
        if fname:
            # Save dir for next time, unless empty str (i.e., use cwd).
            if startpath != "":
                matplotlib.rcParams['savefig.directory'] = (os.path.dirname(fname))
            try:
                self.canvas.figure.savefig(fname)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error saving file", str(e), QtWidgets.QMessageBox.Ok,
                    QtWidgets.QMessageBox.NoButton
                )

    def set_history_buttons(self):
        can_backward = self._nav_stack._pos > 0
        can_forward = self._nav_stack._pos < len(self._nav_stack._elements) - 1
        if 'back' in self._actions:
            self._actions['back'].setEnabled(can_backward)
        if 'forward' in self._actions:
            self._actions['forward'].setEnabled(can_forward)


class SubplotToolQt(UiSubplotTool):
    def __init__(self, targetfig, parent):
        UiSubplotTool.__init__(self, None)

        self._figure = targetfig

        for lower, higher in [("bottom", "top"), ("left", "right")]:
            self._widgets[lower].valueChanged.connect(
                lambda val: self._widgets[higher].setMinimum(val + .001)
            )
            self._widgets[higher].valueChanged.connect(
                lambda val: self._widgets[lower].setMaximum(val - .001)
            )

        self._attrs = ["top", "bottom", "left", "right", "hspace", "wspace"]
        self._defaults = {attr: vars(self._figure.subplotpars)[attr] for attr in self._attrs}

        # Set values after setting the range callbacks, but before setting up
        # the redraw callbacks.
        self._reset()

        for attr in self._attrs:
            self._widgets[attr].valueChanged.connect(self._on_value_changed)
        for action, method in [
            ("Export values", self._export_values), ("Tight layout", self._tight_layout),
            ("Reset", self._reset), ("Close", self.close)
        ]:
            self._widgets[action].clicked.connect(method)

    def _export_values(self):
        # Explicitly round to 3 decimals (which is also the spinbox precision)
        # to avoid numbers of the form 0.100...001.
        dialog = QtWidgets.QDialog()
        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        text = QtWidgets.QPlainTextEdit()
        text.setReadOnly(True)
        layout.addWidget(text)
        text.setPlainText(
            ",\n".join(
                "{}={:.3}".format(attr, self._widgets[attr].value()) for attr in self._attrs
            )
        )
        # Adjust the height of the text widget to fit the whole text, plus
        # some padding.
        size = text.maximumSize()
        size.setHeight(
            QtGui.QFontMetrics(text.document().defaultFont()).size(0, text.toPlainText()).height() +
            20
        )
        text.setMaximumSize(size)
        dialog.exec_()

    def _on_value_changed(self):
        self._figure.subplots_adjust(**{attr: self._widgets[attr].value() for attr in self._attrs})
        self._figure.canvas.draw_idle()

    def _tight_layout(self):
        self._figure.tight_layout()
        for attr in self._attrs:
            widget = self._widgets[attr]
            widget.blockSignals(True)
            widget.setValue(vars(self._figure.subplotpars)[attr])
            widget.blockSignals(False)
        self._figure.canvas.draw_idle()

    def _reset(self):
        for attr, value in self._defaults.items():
            self._widgets[attr].setValue(value)
