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
        self.resize(383, 287)
        self.setModal(True)

	# the 'ok' and 'cancel' buttons
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))


	# select the coincidences with Radio Buttons
        self.coincidenceSingles = QtGui.QRadioButton(self)
        self.coincidenceSingles.setGeometry(QtCore.QRect(210, 50, 145, 28))
        self.coincidenceSingles.setObjectName(_fromUtf8("radioButton"))
        self.coincidenceTwofold = QtGui.QRadioButton(self)
        self.coincidenceTwofold.setGeometry(QtCore.QRect(210, 90, 145, 28))
        self.coincidenceTwofold.setObjectName(_fromUtf8("radioButton_2"))
        self.coincidenceThreefold = QtGui.QRadioButton(self)
        self.coincidenceThreefold.setGeometry(QtCore.QRect(210, 140, 145, 28))
        self.coincidenceThreefold.setObjectName(_fromUtf8("radioButton_3"))
        self.coincidenceFourfold= QtGui.QRadioButton(self)
        self.coincidenceFourfold.setGeometry(QtCore.QRect(210, 180, 145, 28))
        self.coincidenceFourfold.setObjectName(_fromUtf8("radioButton_4"))

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

	# two labels, one for the radio buttons, and one for the checkboxes
        self.labelChannel = QtGui.QLabel(self)
        self.labelChannel.setGeometry(QtCore.QRect(30, 10, 121, 23))
        self.labelChannel.setObjectName(_fromUtf8("label"))


        self.labelCoincidence = QtGui.QLabel(self)
        self.labelCoincidence.setGeometry(QtCore.QRect(210, 10, 121, 23))
        self.labelCoincidence.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(self)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceSingles.setText(tr("Dialog", "Single (No C.)", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceTwofold.setText(tr("Dialog", "Twofold", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceThreefold.setText(tr("Dialog", "Threefold", None, QtGui.QApplication.UnicodeUTF8))
        self.coincidenceFourfold.setText(tr("Dialog", "Fourfould", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan0.setText(tr("Dialog", "Chan0", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan1.setText(tr("Dialog", "Chan1", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan2.setText(tr("Dialog", "Chan2", None, QtGui.QApplication.UnicodeUTF8))
        self.activateChan3.setText(tr("Dialog", "Chan3", None, QtGui.QApplication.UnicodeUTF8))
        self.labelChannel.setText(tr("Dialog", "Use Channel", None, QtGui.QApplication.UnicodeUTF8))
        self.labelCoincidence.setText(tr("Dialog", "Coincidence ", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

