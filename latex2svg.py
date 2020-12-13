# import sys
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtSvg import QSvgWidget

# from io import BytesIO
# import matplotlib.pyplot as plt

# # matplotlib: force computer modern font set
# plt.rc('mathtext', fontset='cm')

# def tex2svg(formula, fontsize=12, dpi=300):
#     """Render TeX formula to SVG.
#     Args:
#         formula (str): TeX formula.
#         fontsize (int, optional): Font size.
#         dpi (int, optional): DPI.
#     Returns:
#         str: SVG render.
#     """

#     fig = plt.figure(figsize=(0.01, 0.01))
#     fig.text(0, 0, r'${}$'.format(formula), fontsize=fontsize)

#     output = BytesIO()
#     fig.savefig(
#         output,
#         dpi=dpi,
#         transparent=True,
#         format='svg',
#         bbox_inches='tight',
#         pad_inches=0.0,
#         frameon=False
#     )
#     plt.close(fig)

#     output.seek(0)
#     return output.read()

# def main():
#     FORMULA = r'\int_{-\infty}^\infty e^{-x^2}\,dx = \sqrt{\pi}'

#     app = QApplication(sys.argv)

#     svg = QSvgWidget()
#     svg.load(tex2svg(FORMULA))
#     svg.show()

#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import rcParams


class MathTextLabel(QtWidgets.QWidget):
    def __init__(self, mathText, parent=None, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent, **kwargs)

        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        r, g, b, a = self.palette().base().color().getRgbF()
        rcParams['font.family'] = "Fira Sans"

        self._figure = Figure(edgecolor=(r, g, b), facecolor=(r, g, b))
        self._canvas = FigureCanvas(self._figure)
        l.addWidget(self._canvas)
        self._figure.clear()
        text = self._figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            size=QtGui.QFont().pointSize() * 2,
        )
        self._canvas.draw()

        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self._figure.set_size_inches(w / 80, h / 80)
        self.setFixedSize(w, h)


if __name__ == '__main__':
    from sys import argv, exit

    class Widget(QtWidgets.QWidget):
        def __init__(self, parent=None, **kwargs):
            super(QtWidgets.QWidget, self).__init__(parent, **kwargs)

            l = QVBoxLayout(self)
            mathText = r'$X_k = \sum_{n=0}^{N-1} x_n . e^{\frac{-i2\pi kn}{N}}$'
            l.addWidget(MathTextLabel(mathText, self), alignment=Qt.AlignHCenter)

    a = QtWidgets.QApplication(argv)
    w = Widget()
    w.show()
    w.raise_()
    exit(a.exec_())

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# # Get window background color
# bg = self.palette().window().color()
# cl = (bg.redF(), bg.greenF(), bg.blueF())

# # Create figure, using window bg color
# self.fig = Figure(edgecolor=cl, facecolor=cl)

# # Add FigureCanvasQTAgg widget to form
# self.canvas = FigureCanvasQTAgg(self.fig)
# self.tex_label_placeholder.layout().addWidget(self.canvas)

# # Clear figure
# self.fig.clear()

# # Set figure title
# self.fig.suptitle('$TeX$', x=0.0, y=0.5, horizontalalignment='left', verticalalignment='center')
# self.canvas.draw()