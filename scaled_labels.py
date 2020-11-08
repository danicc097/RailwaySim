from PyQt5.QtGui import QResizeEvent, QFontMetrics
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
import inspect
"""
#* HOW TO example:

self.all_labels = label_grabber(self)
print(self.all_labels)
size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
for label in self.all_labels:
    label.resizeEvent = ScaledLabel.resizeEvent.__get__(label)
    label.setSizePolicy(size_policy)
    label.setScaledContents(True)
    label.setMinimumSize(label.size())
    label.setMaximumSize(label.size() * 2)
"""


def label_grabber(self):
    """Returns a list of labels from the object"""
    label_list = []
    for name, obj in inspect.getmembers(self):
        if isinstance(obj, QLabel):
            label_list.append(obj)
    return label_list


class ScaledLabel(QLabel):
    def resizeEvent(self, event: QResizeEvent):
        # This flag is used for pixmaps, but I thought it might be useful to
        # disable font scaling. Remove the check if you don't like it.
        if not self.hasScaledContents():
            return

        target_rect = self.contentsRect()
        text = self.text()

        # Use binary search to efficiently find the biggest font that will fit.
        max_size = self.height()
        min_size = 1
        font = self.font()
        while 1 < max_size - min_size:
            new_size = (min_size + max_size) // 2
            font.setPointSize(new_size)
            metrics = QFontMetrics(font)

            # Be careful which overload of boundingRect() you call.
            rect = metrics.boundingRect(target_rect, Qt.AlignLeft, text)
            if (rect.width() > target_rect.width() or rect.height() > target_rect.height()):
                max_size = new_size
            else:
                min_size = new_size

        font.setPointSize(min_size)
        self.setFont(font)