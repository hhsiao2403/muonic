#Created with pyqt designer


from PyQt4 import QtCore, QtGui

tr = QtCore.QCoreApplication.translate


class OptionsDialog(QtGui.QDialog):

    def __init__(self,*args):

        QtGui.QDialog.__init__(self,*args)
        self.resize(380, 196)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20, 150, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.VetoCheckbox = QtGui.QCheckBox(self)
        self.VetoCheckbox.setGeometry(QtCore.QRect(20, 30, 341, 61))
        self.VetoCheckbox.setText(tr("Options", "Emulate Chan3 Software Veto", None, QtGui.QApplication.UnicodeUTF8))

        self.v_box = QtGui.QVBoxLayout()
        self.v_box.addWidget(self.VetoCheckbox)
        self.v_box.addWidget(self.buttonBox)
        self.setLayout(self.v_box)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        windowtitle = QtCore.QString("Options")
        self.setWindowTitle(windowtitle)
        self.show()

if __name__ == "__main__":
    
    import sys
    app = QtGui.QApplication(sys.argv)
    odialog = OptionsDialog()
    sys.exit(app.exec_())

