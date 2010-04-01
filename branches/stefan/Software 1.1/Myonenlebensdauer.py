# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Myonenlebensdauer.ui'
#
# Created: Tue Mar 16 16:27:49 2010
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Myonenlebensdauer(object):
    def setupUi(self, Myonenlebensdauer):
        Myonenlebensdauer.setObjectName("Myonenlebensdauer")
        Myonenlebensdauer.resize(556,346)
        self.dockWidgetContents = QtGui.QWidget(Myonenlebensdauer)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.layoutWidget = QtGui.QWidget(self.dockWidgetContents)
        self.layoutWidget.setGeometry(QtCore.QRect(0,0,551,321))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lcdNumber_2 = QtGui.QLCDNumber(self.layoutWidget)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.horizontalLayout_2.addWidget(self.lcdNumber_2)
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lcdNumber = QtGui.QLCDNumber(self.layoutWidget)
        self.lcdNumber.setObjectName("lcdNumber")
        self.horizontalLayout_2.addWidget(self.lcdNumber)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.layoutWidget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_5 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.pushButton_2 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_4 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_3 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        Myonenlebensdauer.setWidget(self.dockWidgetContents)

        self.retranslateUi(Myonenlebensdauer)
        QtCore.QObject.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.plainTextEdit.clear)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.plainTextEdit.copy)
        QtCore.QMetaObject.connectSlotsByName(Myonenlebensdauer)

    def retranslateUi(self, Myonenlebensdauer):
        Myonenlebensdauer.setWindowTitle(QtGui.QApplication.translate("Myonenlebensdauer", "Myonenlebensdauer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Myonenlebensdauer", "detektierte Myonen", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Myonen pro s", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Auswerten", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Aktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Kopieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Speichern", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Myonenlebensdauer", "Leeren", None, QtGui.QApplication.UnicodeUTF8))

