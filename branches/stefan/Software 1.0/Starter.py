import sys
from PyQt4 import QtCore, QtGui

from threading import Thread

from Aufnahme import Ui_Aufnahme
from AuswertungMyonenfluss import Ui_AuswertungMyonfluss
from AuswertungMyonengeschwindigkeit import Ui_AuswertungMyongeschwindigkeit
from AuswertungMyonenlebensdauer import Ui_AuswertungMyonlebensdauer
from Ereignisse import Ui_Ereignisse
from Hauptfenster import Ui_Hauptfenster
from Koinzidenzmessung import Ui_Koinzidenzmessung
from Myonenfluss import Ui_Myonenfluss
from Myonengeschwindigkeit import Ui_Myonengeschwindigkeit
from Myonenlebensdauer import Ui_Myonenlebensdauer
from Optionen import Ui_TabWidget
from ToTHistogramm import Ui_ToTHistogramm

hauptfenster_show = 1
aufnahme_show = 1
auswertungmyonenfluss_show = 1
auswertungmyonengeschwindigkeit_show = 1
auswertungmyonenlebensdauer_show = 1
ereignisse_show = 1
koinzidenzmessung_show = 1
myonenfluss_show = 1
myonengeschwindigkeit_show = 1
myonenlebensdauer_show = 1
optionen_show = 1
tothistogramm_show = 1

root = QtGui.QApplication(sys.argv)

hauptfenster = QtGui.QMainWindow()
Hauptfenster = Ui_Hauptfenster()
Hauptfenster.setupUi(hauptfenster)
if hauptfenster_show == 1:
    hauptfenster.show()
else:
    hauptfenster.close()
    aufnahme_show = 0
    auswertungmyonenfluss_show = 0
    auswertungmyonengeschwindigkeit_show = 0
    auswertungmyonenlebensdauer_show = 0
    ereignisse_show = 0
    koinzidenzmessung_show = 0  
    myonenfluss_show = 0
    myonengeschwindigkeit_show = 0
    myonenlebensdauer_show = 0
    optionen_show = 0
    tothistogramm_show = 0

aufnahme = QtGui.QDockWidget()
Aufnahme = Ui_Aufnahme()
Aufnahme.setupUi(aufnahme)
if aufnahme_show == 1:
    aufnahme.show()
else:
    aufnahme.close()

auswertungmyonenfluss = QtGui.QFrame()
AuswertungMyonenfluss = Ui_AuswertungMyonfluss()
AuswertungMyonenfluss.setupUi(auswertungmyonenfluss)
if auswertungmyonenfluss_show == 1:
    auswertungmyonenfluss.show()
else:
    auswertungmyonenfluss.close()


auswertungmyonengeschwindigkeit = QtGui.QFrame()
AuswertungMyonengeschwindigkeit = Ui_AuswertungMyongeschwindigkeit()
AuswertungMyonengeschwindigkeit.setupUi(auswertungmyonengeschwindigkeit)
if auswertungmyonengeschwindigkeit_show == 1:
    auswertungmyonengeschwindigkeit.show()
else:
    auswertungmyonengeschwindigkeit.close()

auswertungmyonenlebensdauer = QtGui.QFrame()
AuswertungMyonenlebensdauer = Ui_AuswertungMyonlebensdauer()
AuswertungMyonenlebensdauer.setupUi(auswertungmyonenlebensdauer)
if auswertungmyonenlebensdauer_show == 1:
    auswertungmyonenlebensdauer.show()
else:
    auswertungmyonenlebensdauer.close()

ereignisse = QtGui.QDockWidget()
Ereignisse = Ui_Ereignisse()
Ereignisse.setupUi(ereignisse)
if ereignisse_show == 1:
    ereignisse.show()
else:
    ereignisse.close()

koinzidenzmessung = QtGui.QDockWidget()
Koinzidenzmessung = Ui_Koinzidenzmessung()
Koinzidenzmessung.setupUi(koinzidenzmessung)
if koinzidenzmessung_show == 1:
    koinzidenzmessung.show()
else:
    koinzidenzmessung.close()

myonenfluss = QtGui.QDockWidget()
Myonenfluss = Ui_Myonenfluss()
Myonenfluss.setupUi(myonenfluss)
if myonenfluss_show == 1:
    myonenfluss.show()
else:
    myonenfluss.close()

myonengeschwindigkeit = QtGui.QDockWidget()
Myonengeschwindigkeit = Ui_Myonengeschwindigkeit()
Myonengeschwindigkeit.setupUi(myonengeschwindigkeit)
if myonengeschwindigkeit_show == 1:
    myonengeschwindigkeit.show()
else:
    myonengeschwindigkeit.close()

myonenlebensdauer = QtGui.QDockWidget()
Myonenlebensdauer = Ui_Myonenlebensdauer()
Myonenlebensdauer.setupUi(myonenlebensdauer)
if myonenlebensdauer_show == 1:
    myonenlebensdauer.show()
else:
    myonenlebensdauer.close()

optionen = QtGui.QTabWidget()
Optionen = Ui_TabWidget()
Optionen.setupUi(optionen)
if optionen_show == 1:
    optionen.show()
else:
    optionen.close()

tothistogramm = QtGui.QDockWidget()
ToTHistogramm = Ui_ToTHistogramm()
ToTHistogramm.setupUi(tothistogramm)
if tothistogramm_show == 1:
    tothistogramm.show()
else:
    tothistogramm.close()

root.exec_() 
