import sys
import os
from PyQt5 import QtGui

from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class HyperPDFizer(QObject):
    def __init__(self, input_path, output_path, working_directory=None):
        super().__init__()
        self.input = input_path
        self.output = output_path
        self.cwd = working_directory
        self.profile = QWebEngineProfile()
        self.page = QWebEnginePage(self.profile, None)
        self.page.loadFinished.connect(self.loadFinished)
        self.page.pdfPrintingFinished.connect(self.pdfPrintingFinished)

    def run(self):
        self.page.load(QUrl.fromUserInput(self.input, self.cwd))
        return QApplication.exec()

    def loadFinished(self, ok):
        if not ok:
            print(f"Failed to load URL '{self.input}'", file=sys.stderr, flush=True)
            QCoreApplication.exit(1)
        else:
            psize = QPageSize(QPageSize.A4)
            pmargins = QMarginsF()
            pmargins.setLeft(32)
            pmargins.setRight(32)
            playout = QPageLayout(psize, QPageLayout.Portrait, pmargins)
            self.page.printToPdf(self.output, pageLayout=playout)

    def pdfPrintingFinished(self, file_path, success):
        if not success:
            print(f"Failed to print to output file '{file_path}'", file=sys.stderr, flush=True)
            QCoreApplication.exit(1)
        else:
            print(f"Saved '{self.input}' to '{file_path}'")
            QCoreApplication.quit()


class PrintHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_page = None
        self.m_inPrintPreview = False

    @property
    def page(self):
        return self.m_page

    @page.setter
    def page(self, page):
        if isinstance(page, QWebEnginePage):
            self.m_page = page
            # self.page.printRequested.connect(self.printPreview)
        else:
            raise TypeError("page must be a QWebEnginePage")

    @pyqtSlot()
    def printPreview(self):
        #* Generate PDF in path
        currentdir = os.path.dirname(os.path.realpath(__file__))
        html_path = os.path.join(currentdir, "index.html")
        pdf_path = os.path.join(currentdir, "index.pdf")
        converter = HyperPDFizer(html_path, pdf_path, currentdir)
        converter.run()

        if self.page is None:
            return
        if self.m_inPrintPreview:
            return
        self.m_inPrintPreview = True
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self.page.view())
        preview.paintRequested.connect(self.printDocument)
        preview.exec_()
        self.m_inPrintPreview = False

    @pyqtSlot(QPrinter)
    def printDocument(self, printer):
        result = False
        loop = QEventLoop()

        def printPreview(sucess):
            nonlocal result
            result = sucess
            loop.quit()

        self.page.print(printer, printPreview)
        loop.exec_()
        if not result:
            painter = QPainter()
            if painter.begin(printer):
                font = painter.font()
                font.setPixelSize(20)
                painter.setFont(font)
                painter.drawText(QPointF(10, 25), "Could not generate print preview.")
                painter.end()


BASEDIR = os.path.dirname(__file__)
html_path = os.path.join(BASEDIR, 'index.html')


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        button = QPushButton("PRINT")
        self.view = QWebEngineView()
        url = QUrl.fromLocalFile(html_path)
        self.view.setUrl(url)
        lay = QVBoxLayout(self)
        lay.addWidget(button)
        lay.addWidget(self.view)

        # font.setFamily("Fira Sans Medium")
        # font.setPointSize(10)
        # button.setFont(font)
        self.resize(1000, 880)

        handler = PrintHandler(self)
        handler.page = self.view.page()
        button.clicked.connect(handler.printPreview)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    path = os.path.join(parentDirectory, 'resources', 'fonts', 'Fira_Sans', 'FiraSans-Medium.ttf')
    id = QFontDatabase.addApplicationFont(path)
    family = QFontDatabase.applicationFontFamilies(id)[0]
    font = QFont(family, 14)
    app.setFont(font)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
"""

Python source (proba.py)_________________________________

#!/usr/bin/env python
 
import os
from jinja2 import Environment, FileSystemLoader
 
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)
 
 
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
 
 
def create_index_html():
    fname = "output.html"
    urls = ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
    context = {
        'urls': urls
    }
    #
    with open(fname, 'w') as f:
        html = render_template('index.html', context)
        f.write(html)
 
 
def main():
    create_index_html()
 
########################################
 
if __name__ == "__main__":
    main()



Jinja2 template (templates/index.html)_________________________

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Proba</title>
</head>
<body>
<center>
    <h1>Proba</h1>
    <p>{{ urls|length }} links</p>
</center>
<ol align="left">
{% set counter = 0 -%}
{% for url in urls -%}
<li><a href="{{ url }}">{{ url }}</a></li>
{% set counter = counter + 1 -%}
{% endfor -%}
</ol>
</body>
</html>
Resulting output
If you execute proba.py, you will get this output:

OUT::::::::

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Proba</title>
</head>
<body>
<center>
    <h1>Proba</h1>
    <p>3 links</p>
</center>
<ol align="left">
<li><a href="http://example.com/1">http://example.com/1</a></li>
<li><a href="http://example.com/2">http://example.com/2</a></li>
<li><a href="http://example.com/3">http://example.com/3</a></li>
</ol>
</body>
</html>"""