from PyQt4 import QtGui, QtCore

class ScalarsWindow(QtGui.QDialog): 

    def __init__(self,text, *args):

        _NAME = 'Scalars'
        QtGui.QDialog.__init__(self,*args)
        self.setModal(True)
        self.setWindowTitle("Scalars")
        self.v_box = QtGui.QVBoxLayout()
        self.textbox = QtGui.QPlainTextEdit('')
        self.textbox.setReadOnly(True)
        text_fields = text.split()
        scalars_ch0 = int(text_fields[1][3:],16)
        scalars_ch1 = int(text_fields[2][3:],16)
        scalars_ch2 = int(text_fields[3][3:],16)
        scalars_ch3 = int(text_fields[4][3:],16)
        scalars_trigger = int(text_fields[5][3:],16)
        scalars_time = int(text_fields[6][3:],16)
        scalars_txt = 'Ch0 ' + str(scalars_ch0) + ' rate_0 ' + str(scalars_ch0/scalars_time) + '\n Ch1' + str(scalars_ch1) + ' rate_1 ' + str(scalars_ch1/scalars_time) + '\n Ch2 ' + str(scalars_ch2) + ' rate_2 ' + str(scalars_ch2/scalars_time) +'\n Ch3 ' + str(scalars_ch3) + ' rate_3 ' + str(scalars_ch3/scalars_time) + '\n Trigger ' + str(scalars_trigger) + ' Trigger_rate ' + str(scalars_trigger/scalars_time) + '\n time ' + str(scalars_time) 

        self.textbox.appendPlainText(scalars_txt)
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.v_box.addWidget(self.textbox)
        self.v_box.addWidget(self.button_box)
        self.setLayout(self.v_box)
        QtCore.QObject.connect(self.button_box,
                              QtCore.SIGNAL('accepted()'),
                               self.accept
                              )
        self.show()
