# -*- coding: utf-8 -*-

# created with QT4Designer...

from PyQt4 import QtCore, QtGui

tr = QtGui.QApplication.translate

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class ConfigDialog(QtGui.QDialog):
    def __init__(self, *args):

        QtGui.QDialog.__init__(self,*args)


	# size of window etc..
        self.setObjectName(_fromUtf8("Configure"))
        self.resize(520, 360)
        self.setModal(True)

	# the 'ok' and 'cancel' buttons
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 300, 300, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

	# select the coincidences with Radio Buttons
        # group them in a vertical box, so that they do not
	# collide with the veto radio buttons
        self.vlcoincWid = QtGui.QWidget(self)
        self.vlcoincWid.setGeometry(QtCore.QRect(200, 40, 150, 120))
        self.vlcoincWid.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.vlcoinc = QtGui.QVBoxLayout(self.vlcoincWid)
        self.vlcoinc.setMargin(0)
        self.vlcoinc.setObjectName(_fromUtf8("verticalLayout"))

        self.coincidenceSingles = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceSingles.setGeometry(QtCore.QRect(210, 50, 145, 28))
        self.coincidenceSingles.setObjectName(_fromUtf8("radioButton"))
        self.vlcoinc.addWidget(self.coincidenceSingles)

        self.coincidenceTwofold = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceTwofold.setGeometry(QtCore.QRect(210, 90, 145, 28))
        self.coincidenceTwofold.setObjectName(_fromUtf8("radioButton_2"))
        self.vlcoinc.addWidget(self.coincidenceTwofold)

        self.coincidenceThreefold = QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceThreefold.setGeometry(QtCore.QRect(210, 140, 145, 28))
        self.coincidenceThreefold.setObjectName(_fromUtf8("radioButton_3"))
        self.vlcoinc.addWidget(self.coincidenceThreefold)

        self.coincidenceFourfold= QtGui.QRadioButton(self.vlcoincWid)
        self.coincidenceFourfold.setGeometry(QtCore.QRect(210, 180, 145, 28))
        self.coincidenceFourfold.setObjectName(_fromUtf8("radioButton_4"))
        self.vlcoinc.addWidget(self.coincidenceFourfold)

        # set Veto with RadioButtons
        self.noveto = QtGui.QRadioButton(self)
        self.noveto.setGeometry(QtCore.QRect(410, 50, 145, 28))
        self.noveto.setObjectName(_fromUtf8("radioButton_5"))
        self.vetochan1 = QtGui.QRadioButton(self)
        self.vetochan1.setGeometry(QtCore.QRect(410, 90, 145, 28))
        self.vetochan1.setObjectName(_fromUtf8("radioButton_7"))
        self.vetochan2 = QtGui.QRadioButton(self)
        self.vetochan2.setGeometry(QtCore.QRect(410, 140, 145, 28))
        self.vetochan2.setObjectName(_fromUtf8("radioButton_8"))
        self.vetochan3 = QtGui.QRadioButton(self)
        self.vetochan3.setGeometry(QtCore.QRect(410, 180, 145, 28))
        self.vetochan3.setObjectName(_fromUtf8("radioButton_9"))




	# activate Channels with Checkboxes
        self.activateChan0 = QtGui.QCheckBox(self)
        self.activateChan0.setGeometry(QtCore.QRect(20, 40, 119, 28))
        self.activateChan0.setObjectName(_fromUtf8("checkBox"))
        self.activateChan1 = QtGui.QCheckBox(self)
        self.activateChan1.setGeometry(QtCore.QRect(20, 80, 119, 28))
        self.activateChan1.setObjectName(_fromUtf8("checkBox_2"))
        self.activateChan2 = QtGui.QCheckBox(self)
        self.activateChan2.setGeometry(QtCore.QRect(20, 130, 119, 28))
        self.activateChan2.setObjectName(_fromUtf8("checkBox_3"))
        self.activateChan3 = QtGui.QCheckBox(self)
        self.activateChan3.setGeometry(QtCore.QRect(20, 180, 119, 28))
        self.activateChan3.setObjectName(_fromUtf8("checkBox_4"))

	# three labels, one for the radio buttons, and one for the checkboxes, the last one for veto criterion

        self.labelChannel = QtGui.QLabel(self)
        self.labelChannel.setGeometry(QtCore.QRect(30, 10, 121, 23))
        self.labelChannel.setObjectName(_fromUtf8("label"))


        self.labelCoincidence = QtGui.QLabel(self)
        self.labelCoincidence.setGeometry(QtCore.QRect(210, 10, 121, 23))
        self.labelCoincidence.setObjectName(_fromUtf8("label_2"))

        self.labelVeto = QtGui.QLabel(self)
        self.labelVeto.setGeometry(QtCore.QRect(410, 10, 121, 23))
        self.labelVeto.setObjectName(_fromUtf8("label_veto"))

        self.retranslateUi(self)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceSingles.setText(tr("Dialog", "Single", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceTwofold.setText(tr("Dialog", "Twofold", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceThreefold.setText(tr("Dialog", "Threefold", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceFourfold.setText(tr("Dialog", "Fourfould", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan0.setText(tr("Dialog", "Chan0", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan1.setText(tr("Dialog", "Chan1", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan2.setText(tr("Dialog", "Chan2", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan3.setText(tr("Dialog", "Chan3", None, QtGui.QApplication.UnicodeUTF8))
        self.noveto.setText(tr("Dialog", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.vetochan1.setText(tr("Dialog", "Chan1", None, QtGui.QApplication.UnicodeUTF8))
        self.vetochan2.setText(tr("Dialog", "Chan2", None, QtGui.QApplication.UnicodeUTF8))
        self.vetochan3.setText(tr("Dialog", "Chan3", None, QtGui.QApplication.UnicodeUTF8))
        self.labelChannel.setText(tr("Dialog", "Use Channel", None, QtGui.QApplication.UnicodeUTF8))
        self.labelCoincidence.setText(tr("Dialog", "Coincidence ", None, QtGui.QApplication.UnicodeUTF8))
        self.labelVeto.setText(tr("Dialog", "Use Veto ", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

