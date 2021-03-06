# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RailwaySim_GUI_pref.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(290, 98)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        Form.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cb_dark = QtWidgets.QCheckBox(Form)
        font = QtGui.QFont()
        font.setFamily("Fira Sans Medium")
        font.setPointSize(10)
        self.cb_dark.setFont(font)
        self.cb_dark.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.cb_dark.setObjectName("cb_dark")
        self.verticalLayout.addWidget(self.cb_dark)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cb_watermark = QtWidgets.QCheckBox(Form)
        font = QtGui.QFont()
        font.setFamily("Fira Sans Medium")
        font.setPointSize(10)
        self.cb_watermark.setFont(font)
        self.cb_watermark.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.cb_watermark.setObjectName("cb_watermark")
        self.horizontalLayout.addWidget(self.cb_watermark)
        self.watermark = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.watermark.sizePolicy().hasHeightForWidth())
        self.watermark.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Fira Sans Medium")
        font.setPointSize(10)
        self.watermark.setFont(font)
        self.watermark.setClearButtonEnabled(False)
        self.watermark.setObjectName("watermark")
        self.horizontalLayout.addWidget(self.watermark)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setFamily("Fira Sans Medium")
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Preferences"))
        self.cb_dark.setText(_translate("Form", "Dark theme"))
        self.cb_watermark.setText(_translate("Form", "Chart watermark"))
        self.pushButton.setText(_translate("Form", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
