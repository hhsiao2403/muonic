# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Hauptfenster.ui'
#
# Created: Wed Mar 24 15:21:12 2010
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Hauptfenster(object):
    def setupUi(self, Hauptfenster):
        Hauptfenster.setObjectName("Hauptfenster")
        Hauptfenster.resize(292,313)
        self.centralwidget = QtGui.QWidget(Hauptfenster)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(0,0,291,263))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.checkBox = QtGui.QCheckBox(self.layoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.layoutWidget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        self._2 = QtGui.QHBoxLayout()
        self._2.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self._2.setObjectName("_2")
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self._2.addWidget(self.label_2)
        self.lineEdit = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self._2.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self._2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_2 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        Hauptfenster.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Hauptfenster)
        self.menubar.setGeometry(QtCore.QRect(0,0,292,26))
        self.menubar.setObjectName("menubar")
        self.menuDatei = QtGui.QMenu(self.menubar)
        self.menuDatei.setObjectName("menuDatei")
        self.menuBearbeiten = QtGui.QMenu(self.menubar)
        self.menuBearbeiten.setObjectName("menuBearbeiten")
        self.menuAnsicht = QtGui.QMenu(self.menubar)
        self.menuAnsicht.setObjectName("menuAnsicht")
        self.menuKonsole = QtGui.QMenu(self.menuAnsicht)
        self.menuKonsole.setObjectName("menuKonsole")
        self.menuEinrichtung = QtGui.QMenu(self.menuAnsicht)
        self.menuEinrichtung.setObjectName("menuEinrichtung")
        self.menuMessung = QtGui.QMenu(self.menuAnsicht)
        self.menuMessung.setObjectName("menuMessung")
        self.menuAuswertung_2 = QtGui.QMenu(self.menuAnsicht)
        self.menuAuswertung_2.setObjectName("menuAuswertung_2")
        self.menuExtras = QtGui.QMenu(self.menubar)
        self.menuExtras.setObjectName("menuExtras")
        self.menuAuswertung = QtGui.QMenu(self.menuExtras)
        self.menuAuswertung.setObjectName("menuAuswertung")
        self.menuHilfe = QtGui.QMenu(self.menubar)
        self.menuHilfe.setObjectName("menuHilfe")
        Hauptfenster.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Hauptfenster)
        self.statusbar.setObjectName("statusbar")
        Hauptfenster.setStatusBar(self.statusbar)
        self.action_ffnen = QtGui.QAction(Hauptfenster)
        self.action_ffnen.setObjectName("action_ffnen")
        self.actionNeu = QtGui.QAction(Hauptfenster)
        self.actionNeu.setObjectName("actionNeu")
        self.actionSchlie_en = QtGui.QAction(Hauptfenster)
        self.actionSchlie_en.setObjectName("actionSchlie_en")
        self.actionExportieren = QtGui.QAction(Hauptfenster)
        self.actionExportieren.setObjectName("actionExportieren")
        self.actionImportieren = QtGui.QAction(Hauptfenster)
        self.actionImportieren.setObjectName("actionImportieren")
        self.actionBeenden = QtGui.QAction(Hauptfenster)
        self.actionBeenden.setObjectName("actionBeenden")
        self.actionSprache = QtGui.QAction(Hauptfenster)
        self.actionSprache.setObjectName("actionSprache")
        self.actionOptionen = QtGui.QAction(Hauptfenster)
        self.actionOptionen.setObjectName("actionOptionen")
        self.actionFlu = QtGui.QAction(Hauptfenster)
        self.actionFlu.setObjectName("actionFlu")
        self.actionLebensdauer = QtGui.QAction(Hauptfenster)
        self.actionLebensdauer.setObjectName("actionLebensdauer")
        self.actionGeschwindigkeit = QtGui.QAction(Hauptfenster)
        self.actionGeschwindigkeit.setObjectName("actionGeschwindigkeit")
        self.actionKonsole_2 = QtGui.QAction(Hauptfenster)
        self.actionKonsole_2.setObjectName("actionKonsole_2")
        self.actionBefehle = QtGui.QAction(Hauptfenster)
        self.actionBefehle.setObjectName("actionBefehle")
        self.actionWiederhohlte_Befehle = QtGui.QAction(Hauptfenster)
        self.actionWiederhohlte_Befehle.setObjectName("actionWiederhohlte_Befehle")
        self.actionSpeichern_der_Befehle = QtGui.QAction(Hauptfenster)
        self.actionSpeichern_der_Befehle.setObjectName("actionSpeichern_der_Befehle")
        self.action_ffnen_von_Skript = QtGui.QAction(Hauptfenster)
        self.action_ffnen_von_Skript.setObjectName("action_ffnen_von_Skript")
        self.actionEreignisse = QtGui.QAction(Hauptfenster)
        self.actionEreignisse.setObjectName("actionEreignisse")
        self.actionTOT_Zeiten = QtGui.QAction(Hauptfenster)
        self.actionTOT_Zeiten.setObjectName("actionTOT_Zeiten")
        self.actionWetterdaten_integieren = QtGui.QAction(Hauptfenster)
        self.actionWetterdaten_integieren.setObjectName("actionWetterdaten_integieren")
        self.actionMyonenlebenszeit = QtGui.QAction(Hauptfenster)
        self.actionMyonenlebenszeit.setObjectName("actionMyonenlebenszeit")
        self.actionMyonengeschwindigkeit = QtGui.QAction(Hauptfenster)
        self.actionMyonengeschwindigkeit.setObjectName("actionMyonengeschwindigkeit")
        self.actionMyonenfluss = QtGui.QAction(Hauptfenster)
        self.actionMyonenfluss.setObjectName("actionMyonenfluss")
        self.actionKoinzidenzmessung = QtGui.QAction(Hauptfenster)
        self.actionKoinzidenzmessung.setObjectName("actionKoinzidenzmessung")
        self.actionEreignisse_2 = QtGui.QAction(Hauptfenster)
        self.actionEreignisse_2.setObjectName("actionEreignisse_2")
        self.actionAufnahme = QtGui.QAction(Hauptfenster)
        self.actionAufnahme.setObjectName("actionAufnahme")
        self.actionPython_Konsole = QtGui.QAction(Hauptfenster)
        self.actionPython_Konsole.setObjectName("actionPython_Konsole")
        self.actionEreigniss_Konsole = QtGui.QAction(Hauptfenster)
        self.actionEreigniss_Konsole.setObjectName("actionEreigniss_Konsole")
        self.menuDatei.addAction(self.actionNeu)
        self.menuDatei.addAction(self.action_ffnen)
        self.menuDatei.addAction(self.actionSchlie_en)
        self.menuDatei.addSeparator()
        self.menuDatei.addAction(self.actionExportieren)
        self.menuDatei.addAction(self.actionImportieren)
        self.menuDatei.addSeparator()
        self.menuDatei.addAction(self.actionBeenden)
        self.menuKonsole.addAction(self.actionKonsole_2)
        self.menuKonsole.addAction(self.actionWiederhohlte_Befehle)
        self.menuKonsole.addAction(self.action_ffnen_von_Skript)
        self.menuKonsole.addAction(self.actionSpeichern_der_Befehle)
        self.menuKonsole.addSeparator()
        self.menuKonsole.addAction(self.actionBefehle)
        self.menuKonsole.addSeparator()
        self.menuKonsole.addAction(self.actionPython_Konsole)
        self.menuKonsole.addAction(self.actionEreigniss_Konsole)
        self.menuEinrichtung.addAction(self.actionEreignisse)
        self.menuEinrichtung.addAction(self.actionTOT_Zeiten)
        self.menuEinrichtung.addAction(self.actionKoinzidenzmessung)
        self.menuMessung.addAction(self.actionAufnahme)
        self.menuMessung.addSeparator()
        self.menuMessung.addAction(self.actionEreignisse_2)
        self.menuMessung.addSeparator()
        self.menuMessung.addAction(self.actionWetterdaten_integieren)
        self.menuAuswertung_2.addAction(self.actionMyonenfluss)
        self.menuAuswertung_2.addAction(self.actionMyonenlebenszeit)
        self.menuAuswertung_2.addAction(self.actionMyonengeschwindigkeit)
        self.menuAnsicht.addAction(self.menuKonsole.menuAction())
        self.menuAnsicht.addAction(self.menuEinrichtung.menuAction())
        self.menuAnsicht.addAction(self.menuMessung.menuAction())
        self.menuAnsicht.addAction(self.menuAuswertung_2.menuAction())
        self.menuAuswertung.addAction(self.actionFlu)
        self.menuAuswertung.addAction(self.actionLebensdauer)
        self.menuAuswertung.addAction(self.actionGeschwindigkeit)
        self.menuExtras.addAction(self.actionSprache)
        self.menuExtras.addSeparator()
        self.menuExtras.addAction(self.menuAuswertung.menuAction())
        self.menuExtras.addSeparator()
        self.menuExtras.addAction(self.actionOptionen)
        self.menubar.addAction(self.menuDatei.menuAction())
        self.menubar.addAction(self.menuBearbeiten.menuAction())
        self.menubar.addAction(self.menuAnsicht.menuAction())
        self.menubar.addAction(self.menuExtras.menuAction())
        self.menubar.addAction(self.menuHilfe.menuAction())

        self.retranslateUi(Hauptfenster)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.plainTextEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(Hauptfenster)

    def retranslateUi(self, Hauptfenster):
        Hauptfenster.setWindowTitle(QtGui.QApplication.translate("Hauptfenster", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Hauptfenster", "Konsole", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Hauptfenster", "Autoaktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Hauptfenster", "Befehl", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Hauptfenster", "Leeren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_3.setText(QtGui.QApplication.translate("Hauptfenster", "Aktualisieren", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Hauptfenster", "Senden", None, QtGui.QApplication.UnicodeUTF8))
        self.menuDatei.setTitle(QtGui.QApplication.translate("Hauptfenster", "Datei", None, QtGui.QApplication.UnicodeUTF8))
        self.menuBearbeiten.setTitle(QtGui.QApplication.translate("Hauptfenster", "Bearbeiten", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAnsicht.setTitle(QtGui.QApplication.translate("Hauptfenster", "Ansicht", None, QtGui.QApplication.UnicodeUTF8))
        self.menuKonsole.setTitle(QtGui.QApplication.translate("Hauptfenster", "Konsole", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEinrichtung.setTitle(QtGui.QApplication.translate("Hauptfenster", "Einrichtung", None, QtGui.QApplication.UnicodeUTF8))
        self.menuMessung.setTitle(QtGui.QApplication.translate("Hauptfenster", "Messung", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAuswertung_2.setTitle(QtGui.QApplication.translate("Hauptfenster", "Auswahl", None, QtGui.QApplication.UnicodeUTF8))
        self.menuExtras.setTitle(QtGui.QApplication.translate("Hauptfenster", "Extras", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAuswertung.setTitle(QtGui.QApplication.translate("Hauptfenster", "Auswertung", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHilfe.setTitle(QtGui.QApplication.translate("Hauptfenster", "Hilfe", None, QtGui.QApplication.UnicodeUTF8))
        self.action_ffnen.setText(QtGui.QApplication.translate("Hauptfenster", "Öffnen", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNeu.setText(QtGui.QApplication.translate("Hauptfenster", "Neu", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSchlie_en.setText(QtGui.QApplication.translate("Hauptfenster", "Schließen", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExportieren.setText(QtGui.QApplication.translate("Hauptfenster", "Exportieren", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImportieren.setText(QtGui.QApplication.translate("Hauptfenster", "Importieren", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBeenden.setText(QtGui.QApplication.translate("Hauptfenster", "Beenden", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSprache.setText(QtGui.QApplication.translate("Hauptfenster", "Sprache", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOptionen.setText(QtGui.QApplication.translate("Hauptfenster", "Optionen", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFlu.setText(QtGui.QApplication.translate("Hauptfenster", "Myonenfluß", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLebensdauer.setText(QtGui.QApplication.translate("Hauptfenster", "Myonenlebensdauer", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGeschwindigkeit.setText(QtGui.QApplication.translate("Hauptfenster", "Myonengeschwindigkeit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionKonsole_2.setText(QtGui.QApplication.translate("Hauptfenster", "Konsole", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBefehle.setText(QtGui.QApplication.translate("Hauptfenster", "Befehlsindex", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWiederhohlte_Befehle.setText(QtGui.QApplication.translate("Hauptfenster", "Wiederholte Befehle", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSpeichern_der_Befehle.setText(QtGui.QApplication.translate("Hauptfenster", "Speichern der Befehle", None, QtGui.QApplication.UnicodeUTF8))
        self.action_ffnen_von_Skript.setText(QtGui.QApplication.translate("Hauptfenster", "Öffnen von Skript", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEreignisse.setText(QtGui.QApplication.translate("Hauptfenster", "Ereignisse", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTOT_Zeiten.setText(QtGui.QApplication.translate("Hauptfenster", "ToT - Histogramm", None, QtGui.QApplication.UnicodeUTF8))
        self.actionWetterdaten_integieren.setText(QtGui.QApplication.translate("Hauptfenster", "Wetterdaten einbeziehen", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMyonenlebenszeit.setText(QtGui.QApplication.translate("Hauptfenster", "Myonenlebensdauer", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMyonengeschwindigkeit.setText(QtGui.QApplication.translate("Hauptfenster", "Myonengeschwindigkeit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMyonenfluss.setText(QtGui.QApplication.translate("Hauptfenster", "Myonenfluss", None, QtGui.QApplication.UnicodeUTF8))
        self.actionKoinzidenzmessung.setText(QtGui.QApplication.translate("Hauptfenster", "Koinzidenzmessung", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEreignisse_2.setText(QtGui.QApplication.translate("Hauptfenster", "Ereignisse", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAufnahme.setText(QtGui.QApplication.translate("Hauptfenster", "Aufnahme", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPython_Konsole.setText(QtGui.QApplication.translate("Hauptfenster", "Python-Konsole", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEreigniss_Konsole.setText(QtGui.QApplication.translate("Hauptfenster", "Ereigniss-Konsole", None, QtGui.QApplication.UnicodeUTF8))


class Hauptfenster(QtGui.QMainWindow, Ui_Hauptfenster):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

        self.setupUi(self)

