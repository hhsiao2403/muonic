#! /usr/bin/env python


from PyQt4 import QtGui, QtCore
from helptext import helper


class HelpWindow(QtGui.QDialog): 

    def __init__(self, *args):
        _NAME = 'Help'
        QtGui.QDialog.__init__(self,*args)
        self.resize(600, 480)
        self.setModal(True)
        self.setWindowTitle("DAQ Commands")
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QPlainTextEdit(helper)
        self.textbox.setReadOnly(True)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )


        self.show()

if __name__ == "__main__":

    import sys
    app = QtGui.QApplication(sys.argv)
    hwindow = HelpWindow()
    sys.exit(app.exec_())

