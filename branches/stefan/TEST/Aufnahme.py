# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Aufnahme.ui'
#
# Created: Tue Mar 16 16:25:02 2010
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Aufnahme(object):
    def setupUi(self, Aufnahme):
        Aufnahme.setObjectName("Aufnahme")
        Aufnahme.resize(151,269)
        self.dockWidgetContents = QtGui.QWidget(Aufnahme)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.widget = QtGui.QWidget(self.dockWidgetContents)
        self.widget.setGeometry(QtCore.QRect(0,0,151,244))
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.pushButton_3 = QtGui.QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_2 = QtGui.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox = QtGui.QCheckBox(self.widget)
        self.checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.progressBar_2 = QtGui.QProgressBar(self.widget)
        self.progressBar_2.setProperty("value",QtCore.QVariant(24))
        self.progressBar_2.setObjectName("progressBar_2")
        self.verticalLayout.addWidget(self.progressBar_2)
        self.line_2 = QtGui.QFrame(self.widget)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout.addWidget(self.line_2)
        self.checkBox_2 = QtGui.QCheckBox(self.widget)
        self.checkBox_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.progressBar = QtGui.QProgressBar(self.widget)
        self.progressBar.setProperty("value",QtCore.QVariant(24))
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        Aufnahme.setWidget(self.dockWidgetContents)

        self.retranslateUi(Aufnahme)
        QtCore.QMetaObject.connectSlotsByName(Aufnahme)

    def retranslateUi(self, Aufnahme):
        Aufnahme.setWindowTitle(QtGui.QApplication.translate("Aufnahme", "Aufnahme", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Aufnahme", "Aufnahme starten", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Aufnahme", "Aufnahme abbrechen", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Aufnahme", "Aufnahme beenden", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Aufnahme", "Timer ein", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("Aufnahme", "Simulation", None, QtGui.QApplication.UnicodeUTF8))

