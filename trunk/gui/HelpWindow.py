
from PyQt4 import QtGui, QtCore
from helptext import helper

#class HelpWindow(QtGui.QWidget): 

    #def __init__(self, parent=None): 
        #QtGui.QWidget.__init__(self, parent) 
        #self.font = QtGui.QFont("Helvetica", 16) 
        #elf.pen = QtGui.QPen(QtGui.QColor(0,0,255))

class HelpWindow(QtGui.QDialog): 
    def __init__(self, *args):
        _NAME = 'Help'
        QtGui.QDialog.__init__(self,*args)
        self.resize(640, 480)
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

    #def paintEvent(self, event): 
        #painter = QtGui.QPainter(self) 
        #painter.setPen(self.pen) 
        #painter.setFont(self.font) 
        #painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Help not available yet!")



