#Created with pyqt designer


from PyQt4 import QtCore, QtGui

tr = QtCore.QCoreApplication.translate


class ChooseDecayTriggerDialog(QtGui.QDialog):

    def __init__(self,*args):

        QtGui.QDialog.__init__(self,*args)
        self.resize(380, 196)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20, 150, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        self.DecayTriggerSimple = QtGui.QRadioButton(self)
        self.DecayTriggerSimple.setGeometry(QtCore.QRect(20, 30, 341, 61))
        self.DecayTriggerSimple.setText(tr("Choose decay trigger", "Just look for two triggers in 20 micsec, threefold coincidence, chan3 is veto", None, QtGui.QApplication.UnicodeUTF8))

        self.DecayTriggerSingle = QtGui.QRadioButton(self)
        self.DecayTriggerSingle.setGeometry(QtCore.QRect(20, 30, 341, 61))
        self.DecayTriggerSingle.setText(tr("Choose decay trigger", "Just look for two pulses in 20 micsec, no Veto/Coincidence criterion applied", None, QtGui.QApplication.UnicodeUTF8))
        self.DecayTriggerThorough = QtGui.QRadioButton(self)
        self.DecayTriggerThorough.setGeometry(QtCore.QRect(20, 30, 341, 61))
        self.DecayTriggerThorough.setText(tr("Choose decay trigger", "A thorough trigger: The second pulse must be in the same channel like the first pulse, window is again 20 micsec, no Veto/Coincidence criterion applied", None, QtGui.QApplication.UnicodeUTF8))

        self.v_box = QtGui.QVBoxLayout()
        self.v_box.addWidget(self.DecayTriggerSimple)
        self.v_box.addWidget(self.DecayTriggerSingle)
        self.v_box.addWidget(self.DecayTriggerThorough)
        self.v_box.addWidget(self.buttonBox)
        self.setLayout(self.v_box)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        windowtitle = QtCore.QString("Choose decay trigger")
        self.setWindowTitle(windowtitle)
        self.show()

if __name__ == "__main__":
    
    import sys
    app = QtGui.QApplication(sys.argv)
    odialog = ChooseDecayTriggerDialog()
    sys.exit(app.exec_())

