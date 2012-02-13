from PyQt4 import QtGui
from PyQt4 import QtCore

class PeriodicCallDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QLineEdit()
        self.time_box = QtGui.QSpinBox()
        self.time_box.setMaximum(600)
        self.time_box.setMinimum(1)
        self.time_box.setSingleStep(1)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.time_box)
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
    
# vim: ai ts=4 sts=4 et sw=4
