from PyQt4 import QtGui
from PyQt4 import QtCore

class ThresholdDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.v_box = QtGui.QVBoxLayout()
        self.ch0_input = QtGui.QLineEdit()
        self.ch1_input = QtGui.QLineEdit()
        self.ch2_input = QtGui.QLineEdit()
        self.ch3_input = QtGui.QLineEdit()
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.ch0)
        self.v_box.addWidget(self.ch1)
        self.v_box.addWidget(self.ch2)
        self.v_box.addWidget(self.ch3)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('rejected()'),
                              self.reject)
        self.show()
