from PyQt4 import QtGui, QtCore

class ScalarsWindow(QtGui.QDialog): 

    def __init__(self,inqueue,outqueue, *args):

        def readout_daqscalars():
            inqueue,outqueue
            outqueue.put("SD")
            #return str(inqueue.get(0))
            return 'TEST'

        _NAME = 'Scalars'
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.setWindowTitle("Scalars")
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QPlainTextEdit('')
        self.textbox.setReadOnly(True)
        self.textbox.appendPlainText(readout_daqscalars())
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )
        self.show()
