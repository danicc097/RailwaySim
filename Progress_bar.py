#
# ! See "The Manager" section - Fitzpatrick

import time
from PyQt5.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import sys


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    progress
    int progress complete,from 0-100
    """
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker threadInherits from QRunnable to handle worker thread setup, signals
    and wrap-up.
    """
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        total_n = 1000
        for n in range(total_n):
            progress_pc = int(100 * float(n + 1) / total_n)
            self.signals.progress.emit(progress_pc)
            time.sleep(0.01)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.progress = QProgressBar()
        button = QPushButton("START IT UP")
        button.pressed.connect(self.execute)
        layout.addWidget(self.progress)
        layout.addWidget(button)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def execute(self):
        worker = Worker()
        worker.signals.progress.connect(self.update_progress)
        # Execute
        self.threadpool.start(worker)

    def update_progress(self, progress):
        self.progress.setValue(progress)


app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
