# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RailwaySim_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(819, 591)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMaximumSize(QtCore.QSize(833, 559))
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(200)
        sizePolicy.setVerticalStretch(200)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setSizeIncrement(QtCore.QSize(20, 20))
        self.tabWidget.setBaseSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setAcceptDrops(False)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.rolling = QtWidgets.QWidget()
        self.rolling.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rolling.sizePolicy().hasHeightForWidth())
        self.rolling.setSizePolicy(sizePolicy)
        self.rolling.setMinimumSize(QtCore.QSize(795, 0))
        self.rolling.setMaximumSize(QtCore.QSize(804, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.rolling.setFont(font)
        self.rolling.setAccessibleName("")
        self.rolling.setAccessibleDescription("")
        self.rolling.setObjectName("rolling")
        self.formLayout = QtWidgets.QFormLayout(self.rolling)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(self.rolling)
        self.groupBox_2.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(True)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_14.addWidget(self.label_14)
        self.doubleSpinBox_11 = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_11.setWrapping(False)
        self.doubleSpinBox_11.setSpecialValueText("")
        self.doubleSpinBox_11.setMaximum(9.99)
        self.doubleSpinBox_11.setSingleStep(0.25)
        self.doubleSpinBox_11.setObjectName("doubleSpinBox_11")
        self.horizontalLayout_14.addWidget(self.doubleSpinBox_11)
        self.gridLayout_2.addLayout(self.horizontalLayout_14, 2, 1, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_13.addWidget(self.label_13)
        self.doubleSpinBox_10 = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_10.setWrapping(False)
        self.doubleSpinBox_10.setSpecialValueText("")
        self.doubleSpinBox_10.setPrefix("")
        self.doubleSpinBox_10.setObjectName("doubleSpinBox_10")
        self.horizontalLayout_13.addWidget(self.doubleSpinBox_10)
        self.gridLayout_2.addLayout(self.horizontalLayout_13, 4, 0, 1, 1)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_15 = QtWidgets.QLabel(self.groupBox_5)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_15.addWidget(self.label_15)
        self.spinBox_3 = QtWidgets.QSpinBox(self.groupBox_5)
        self.spinBox_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_3.setWrapping(False)
        self.spinBox_3.setSpecialValueText("")
        self.spinBox_3.setObjectName("spinBox_3")
        self.horizontalLayout_15.addWidget(self.spinBox_3)
        self.gridLayout_2.addLayout(self.horizontalLayout_15, 0, 0, 1, 1)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_9 = QtWidgets.QLabel(self.groupBox_5)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_11.addWidget(self.label_9)
        self.doubleSpinBox_8 = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_8.setWrapping(False)
        self.doubleSpinBox_8.setSpecialValueText("")
        self.doubleSpinBox_8.setPrefix("")
        self.doubleSpinBox_8.setMaximum(999.0)
        self.doubleSpinBox_8.setObjectName("doubleSpinBox_8")
        self.horizontalLayout_11.addWidget(self.doubleSpinBox_8)
        self.gridLayout_2.addLayout(self.horizontalLayout_11, 2, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_12.addWidget(self.label_12)
        self.doubleSpinBox_9 = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_9.setWrapping(False)
        self.doubleSpinBox_9.setSpecialValueText("")
        self.doubleSpinBox_9.setPrefix("")
        self.doubleSpinBox_9.setObjectName("doubleSpinBox_9")
        self.horizontalLayout_12.addWidget(self.doubleSpinBox_9)
        self.gridLayout_2.addLayout(self.horizontalLayout_12, 3, 0, 1, 1)
        self.horizontalLaya_2 = QtWidgets.QHBoxLayout()
        self.horizontalLaya_2.setObjectName("horizontalLaya_2")
        self.label_16 = QtWidgets.QLabel(self.groupBox_5)
        self.label_16.setObjectName("label_16")
        self.horizontalLaya_2.addWidget(self.label_16)
        self.spinBox_11 = QtWidgets.QSpinBox(self.groupBox_5)
        self.spinBox_11.setWrapping(False)
        self.spinBox_11.setSpecialValueText("")
        self.spinBox_11.setMaximum(999)
        self.spinBox_11.setObjectName("spinBox_11")
        self.horizontalLaya_2.addWidget(self.spinBox_11)
        self.gridLayout_2.addLayout(self.horizontalLaya_2, 0, 1, 1, 1)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.label_18 = QtWidgets.QLabel(self.groupBox_5)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_17.addWidget(self.label_18)
        self.spinBox_5 = QtWidgets.QSpinBox(self.groupBox_5)
        self.spinBox_5.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_5.setWrapping(False)
        self.spinBox_5.setSpecialValueText("")
        self.spinBox_5.setObjectName("spinBox_5")
        self.horizontalLayout_17.addWidget(self.spinBox_5)
        self.gridLayout_2.addLayout(self.horizontalLayout_17, 3, 1, 1, 1)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_17 = QtWidgets.QLabel(self.groupBox_5)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_16.addWidget(self.label_17)
        self.spinBox_4 = QtWidgets.QSpinBox(self.groupBox_5)
        self.spinBox_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_4.setWrapping(False)
        self.spinBox_4.setSpecialValueText("")
        self.spinBox_4.setObjectName("spinBox_4")
        self.horizontalLayout_16.addWidget(self.spinBox_4)
        self.gridLayout_2.addLayout(self.horizontalLayout_16, 4, 1, 1, 1)
        self.horizontalLayout_20.addWidget(self.groupBox_5)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.rolling)
        self.groupBox.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox.setFont(font)
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(True)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.label_19 = QtWidgets.QLabel(self.groupBox_3)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_18.addWidget(self.label_19)
        self.spinBox_6 = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_6.setWrapping(False)
        self.spinBox_6.setSpecialValueText("")
        self.spinBox_6.setObjectName("spinBox_6")
        self.horizontalLayout_18.addWidget(self.spinBox_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_18)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setWrapping(False)
        self.spinBox.setSpecialValueText("")
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.spinBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_2.setWrapping(False)
        self.doubleSpinBox_2.setSpecialValueText("")
        self.doubleSpinBox_2.setPrefix("")
        self.doubleSpinBox_2.setMaximum(999.0)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.doubleSpinBox_3 = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_3.setWrapping(False)
        self.doubleSpinBox_3.setSpecialValueText("")
        self.doubleSpinBox_3.setPrefix("")
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.horizontalLayout_3.addWidget(self.doubleSpinBox_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_4.setWrapping(False)
        self.doubleSpinBox_4.setSpecialValueText("")
        self.doubleSpinBox_4.setPrefix("")
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.horizontalLayout_4.addWidget(self.doubleSpinBox_4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLaya = QtWidgets.QHBoxLayout()
        self.horizontalLaya.setObjectName("horizontalLaya")
        self.label_11 = QtWidgets.QLabel(self.groupBox_3)
        self.label_11.setObjectName("label_11")
        self.horizontalLaya.addWidget(self.label_11)
        self.spinBox_10 = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox_10.setWrapping(False)
        self.spinBox_10.setSpecialValueText("")
        self.spinBox_10.setMaximum(999)
        self.spinBox_10.setObjectName("spinBox_10")
        self.horizontalLaya.addWidget(self.spinBox_10)
        self.verticalLayout_2.addLayout(self.horizontalLaya)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_7.addWidget(self.label_8)
        self.doubleSpinBox_7 = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_7.setWrapping(False)
        self.doubleSpinBox_7.setSpecialValueText("")
        self.doubleSpinBox_7.setMaximum(9.99)
        self.doubleSpinBox_7.setSingleStep(0.25)
        self.doubleSpinBox_7.setObjectName("doubleSpinBox_7")
        self.horizontalLayout_7.addWidget(self.doubleSpinBox_7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_10.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_7 = QtWidgets.QLabel(self.groupBox_4)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_8.addWidget(self.label_7)
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_2.setWrapping(False)
        self.spinBox_2.setSpecialValueText("")
        self.spinBox_2.setObjectName("spinBox_2")
        self.horizontalLayout_8.addWidget(self.spinBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.groupBox_4)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_5.setWrapping(False)
        self.doubleSpinBox_5.setSpecialValueText("")
        self.doubleSpinBox_5.setPrefix("")
        self.doubleSpinBox_5.setMaximum(999.0)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.horizontalLayout_5.addWidget(self.doubleSpinBox_5)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_6 = QtWidgets.QLabel(self.groupBox_4)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.doubleSpinBox_6 = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_6.setWrapping(False)
        self.doubleSpinBox_6.setSpecialValueText("")
        self.doubleSpinBox_6.setPrefix("")
        self.doubleSpinBox_6.setObjectName("doubleSpinBox_6")
        self.horizontalLayout_6.addWidget(self.doubleSpinBox_6)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.label_20 = QtWidgets.QLabel(self.groupBox_4)
        self.label_20.setObjectName("label_20")
        self.horizontalLayout_19.addWidget(self.label_20)
        self.spinBox_7 = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox_7.setWrapping(False)
        self.spinBox_7.setSpecialValueText("")
        self.spinBox_7.setObjectName("spinBox_7")
        self.horizontalLayout_19.addWidget(self.spinBox_7)
        self.verticalLayout_3.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_10.addWidget(self.groupBox_4)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout_3)
        self.pushButton = QtWidgets.QPushButton(self.rolling)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton)
        self.tabWidget.addTab(self.rolling, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setMinimumSize(QtCore.QSize(0, 502))
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.route = QtWidgets.QWidget()
        self.route.setObjectName("route")
        self.tabWidget.addTab(self.route, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.Sim = QtWidgets.QWidget()
        self.Sim.setObjectName("Sim")
        self.tabWidget.addTab(self.Sim, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 819, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionNew_Window = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:/OneDrive/RailwaySim/Qt/images/png/doc_new_icon&48.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew_Window.setIcon(icon)
        self.actionNew_Window.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.actionNew_Window.setObjectName("actionNew_Window")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("D:/OneDrive/RailwaySim/Qt/images/png/folder_open_icon&48.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("D:/OneDrive/RailwaySim/Qt/images/png/save_icon&48.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_as = QtWidgets.QAction(MainWindow)
        self.actionSave_as.setObjectName("actionSave_as")
        self.actionGitHub_Homepage = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("D:/OneDrive/RailwaySim/Qt/images/github icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGitHub_Homepage.setIcon(icon3)
        self.actionGitHub_Homepage.setObjectName("actionGitHub_Homepage")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("D:/OneDrive/RailwaySim/Qt/images/png/doc_edit_icon&48.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreferences.setIcon(icon4)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionExi = QtWidgets.QAction(MainWindow)
        self.actionExi.setObjectName("actionExi")
        self.menuFile.addAction(self.actionNew_Window)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExi)
        self.menuEdit.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionGitHub_Homepage)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rolling.setWhatsThis(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Passenger train simulation"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Car"))
        self.label_14.setText(_translate("MainWindow", "Maximum acceleration"))
        self.doubleSpinBox_11.setSuffix(_translate("MainWindow", " m/s²"))
        self.label_13.setText(_translate("MainWindow", "Frontal area"))
        self.doubleSpinBox_10.setSuffix(_translate("MainWindow", " m²"))
        self.label_15.setText(_translate("MainWindow", "Number"))
        self.spinBox_3.setSuffix(_translate("MainWindow", " u"))
        self.label_9.setText(_translate("MainWindow", "Train mass"))
        self.doubleSpinBox_8.setSuffix(_translate("MainWindow", " t"))
        self.label_12.setText(_translate("MainWindow", "Running mass "))
        self.doubleSpinBox_9.setSuffix(_translate("MainWindow", " %"))
        self.label_16.setText(_translate("MainWindow", "Maximum speed"))
        self.spinBox_11.setSuffix(_translate("MainWindow", " km/h"))
        self.label_18.setText(_translate("MainWindow", "Bogies"))
        self.spinBox_5.setSuffix(_translate("MainWindow", " u"))
        self.label_17.setText(_translate("MainWindow", "Motorized bogies"))
        self.spinBox_4.setSuffix(_translate("MainWindow", " u"))
        self.groupBox.setTitle(_translate("MainWindow", "Locomotive simulation"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Locomotive"))
        self.label_19.setText(_translate("MainWindow", "Axles"))
        self.spinBox_6.setSuffix(_translate("MainWindow", " u"))
        self.label.setText(_translate("MainWindow", "Number"))
        self.spinBox.setSuffix(_translate("MainWindow", " u"))
        self.label_2.setText(_translate("MainWindow", "Individual mass"))
        self.doubleSpinBox_2.setSuffix(_translate("MainWindow", " t"))
        self.label_3.setText(_translate("MainWindow", "Running mass "))
        self.doubleSpinBox_3.setSuffix(_translate("MainWindow", " %"))
        self.label_4.setText(_translate("MainWindow", "Frontal area"))
        self.doubleSpinBox_4.setSuffix(_translate("MainWindow", " m²"))
        self.label_11.setText(_translate("MainWindow", "Maximum speed"))
        self.spinBox_10.setSuffix(_translate("MainWindow", " km/h"))
        self.label_8.setText(_translate("MainWindow", "Maximum acceleration"))
        self.doubleSpinBox_7.setSuffix(_translate("MainWindow", " m/s²"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Wagon"))
        self.label_7.setText(_translate("MainWindow", "Number"))
        self.spinBox_2.setSuffix(_translate("MainWindow", " u"))
        self.label_5.setText(_translate("MainWindow", "Individual mass"))
        self.doubleSpinBox_5.setSuffix(_translate("MainWindow", " t"))
        self.label_6.setText(_translate("MainWindow", "Running mass "))
        self.doubleSpinBox_6.setSuffix(_translate("MainWindow", " %"))
        self.label_20.setText(_translate("MainWindow", "Axles"))
        self.spinBox_7.setSuffix(_translate("MainWindow", " u"))
        self.pushButton.setText(_translate("MainWindow", "Validate data"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rolling), _translate("MainWindow", "Rolling stock"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Rolling resistance"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.route), _translate("MainWindow", "Route"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Page"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Sim), _translate("MainWindow", "Simulation"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionNew_Window.setText(_translate("MainWindow", "New Window"))
        self.actionNew_Window.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "Open..."))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_as.setText(_translate("MainWindow", "Save as..."))
        self.actionSave_as.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionGitHub_Homepage.setText(_translate("MainWindow", "GitHub Homepage"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionExi.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
