# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Myonenfluss.ui'
#
# Created: Tue Mar 16 16:27:18 2010
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Myonenfluss(object):
    def setupUi(self, Myonenfluss):
        Myonenfluss.setObjectName("Myonenfluss")
        Myonenfluss.resize(556,346)
        self.dockWidgetContents = QtGui.QWidget(Myonenfluss)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.widget = QtGui.QWidget(self.dockWidgetContents)
        self.widget.setGeometry(QtCore.QRect(0,0,551,321))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.lcdNumber_2 = QtGui.QLCDNumber(self.widget)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.horizontalLayout_2.addWidget(self.lcdNumber_2)
        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lcdNumber = QtGui.QLCDNumber(self.widget)
        self.lcdNumber.setObjectName("lcdNumber")
        self.horizontalLayout_2.addWidget(self.lcdNumber)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.widget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_5 = QtGui.QPushButton(self.widget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.pushButton_2 = QtGui.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_4 = QtGui.QPushButton(self.widget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_3 = QtGui.QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        Myonenfluss.setWidget(self.dockWidgetContents)

        self.retranslateUi(Myonenfluss)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.plainTextEdit.copy)
        QtCore.QObject.connect(self.pushButton_3,QtCore.SIGNAL("clicked()"),self.plainTextEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(Myonenfluss)

    def retranslateUi(self, Myonenfluss):
        Myonenfluss.setWindowTitle(QtGui.QApplication.translate("Myonenfluss", "Myonenfluss", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Myonenfluss", "detektierte Myonen", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Myonenfluss", "Myonen pro s", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Myonenfluss", "Auswerten", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("Myonenfluss", "Aktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Myonenfluss", "Kopieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("Myonenfluss", "Speichern", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Myonenfluss", "Leeren", None, QtGui.QApplication.UnicodeUTF8))

