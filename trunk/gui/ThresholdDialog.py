from PyQt4 import QtGui
from PyQt4 import QtCore

tr = QtCore.QCoreApplication.translate


class ThresholdDialog(QtGui.QDialog):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self,*args)
        self.setWindowTitle("Threshold Settings")
        self.resize(260, 260)     
        self.setModal(True)
        self.label0 = QtGui.QLabel()
        self.label0.setText(tr("Dialog", "Chan0"))
        self.label1 = QtGui.QLabel()
        self.label1.setText(tr("Dialog", "Chan1"))
        self.label2 = QtGui.QLabel()
        self.label2.setText(tr("Dialog", "Chan2"))
        self.label3 = QtGui.QLabel()
        self.label3.setText(tr("Dialog", "Chan3"))

        self.v_box = QtGui.QVBoxLayout()
        self.ch0_input = QtGui.QLineEdit()
        self.ch1_input = QtGui.QLineEdit()
        self.ch2_input = QtGui.QLineEdit()
        self.ch3_input = QtGui.QLineEdit()
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.v_box.addWidget(self.label0)
        self.v_box.addWidget(self.ch0_input)
        self.v_box.addWidget(self.label1)
        self.v_box.addWidget(self.ch1_input)
        self.v_box.addWidget(self.label2)
        self.v_box.addWidget(self.ch2_input)
        self.v_box.addWidget(self.label3)
        self.v_box.addWidget(self.ch3_input)
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
