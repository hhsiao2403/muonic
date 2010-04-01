# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AuswertungMyonenlebensdauer.ui'
#
# Created: Wed Mar 17 13:42:03 2010
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AuswertungMyonlebensdauer(object):
    def setupUi(self, AuswertungMyonlebensdauer):
        AuswertungMyonlebensdauer.setObjectName("AuswertungMyonlebensdauer")
        AuswertungMyonlebensdauer.resize(589,508)
        AuswertungMyonlebensdauer.setFrameShape(QtGui.QFrame.StyledPanel)
        AuswertungMyonlebensdauer.setFrameShadow(QtGui.QFrame.Raised)
        self.layoutWidget = QtGui.QWidget(AuswertungMyonlebensdauer)
        self.layoutWidget.setGeometry(QtCore.QRect(10,10,571,491))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lcdNumber = QtGui.QLCDNumber(self.layoutWidget)
        self.lcdNumber.setObjectName("lcdNumber")
        self.horizontalLayout.addWidget(self.lcdNumber)
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.graphicsView = QtGui.QGraphicsView(self.layoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBox = QtGui.QCheckBox(self.layoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(AuswertungMyonlebensdauer)
        QtCore.QMetaObject.connectSlotsByName(AuswertungMyonlebensdauer)

    def retranslateUi(self, AuswertungMyonlebensdauer):
        AuswertungMyonlebensdauer.setWindowTitle(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "Auswertung Myonlebensdauer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "stecken gebliebene Myonen", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "mittlere Lebensdauer", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "Autoaktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", " Aktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "Kopieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("AuswertungMyonlebensdauer", "Speichern", None, QtGui.QApplication.UnicodeUTF8))

