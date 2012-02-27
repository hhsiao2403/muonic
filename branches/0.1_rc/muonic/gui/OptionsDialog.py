#Created with pyqt designer


from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class OptionsDialog(QtGui.QDialog):
    def __init__(self,*args):

        QtGui.QDialog.__init__(self,*args)


    #def setupUi(self, Dialog):
        #Dialog.setObjectName(_fromUtf8("Options"))
        #Dialog.resize(380, 196)
        self.setObjectName(_fromUtf8("Options"))
        self.resize(380, 196)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20, 150, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.CpldCheckbox = QtGui.QCheckBox(self)
        self.CpldCheckbox.setGeometry(QtCore.QRect(20, 30, 341, 61))
        self.CpldCheckbox.setObjectName(_fromUtf8("checkBox"))
        self.VetoCheckbox = QtGui.QCheckBox(self)
        self.VetoCheckbox.setGeometry(QtCore.QRect(20, 110, 311, 28))
        self.VetoCheckbox.setObjectName(_fromUtf8("checkBox_2"))

        self.retranslateUi(self)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Dialog):
        self.setWindowTitle(QtGui.QApplication.translate("Options", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.CpldCheckbox.setText(QtGui.QApplication.translate("Options", "Use DAQ CPLD clock rather \n"
" than software clock  \n"
" for rate calculation", None, QtGui.QApplication.UnicodeUTF8))
        self.VetoCheckbox.setText(QtGui.QApplication.translate("Options", "Emulate Chan3 Software Veto", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = OptionsDialog()
    #ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

