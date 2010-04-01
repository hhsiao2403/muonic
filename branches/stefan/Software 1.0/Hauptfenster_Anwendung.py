import sys
from PyQt4 import QtCore, QtGui


class hauptfenster_anwendung():
    
    def action_ffnen_clicked(self):
        filename = QtGui.QFileDialog.getOpenFileName()
        file=open(filename)
        data = file.read()
        
    def actionNeu_clicked(self):
        filename = QtGui.QFileDialog.getSaveFileName()
        file=save(filename)
        data = file.write()        
        
    def Schlie_en_clicked(self):
        pass  
   
    def actionAktualisieren(self):
        pass
  
    def actionAutoAktualisieren(self):
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.actionAktualisieren)
        self.timer.start(100)
    
    def actionSend_clicked(self):
        text = str(self.lineEdit.displayText())
        if len(text) > 0:
            self.outqueue.put(str(self.lineEdit.displayText()))
            self.lineEdit.add_hist_item(text)
            self.lineEdit.clear()

    def processIncoming(self):
        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                self.plainTextEdit.appendPlainText(str(msg))
                if self.write_file:
                    self.outputfile.write(str(msg)+'\n')
            except Queue.Empty:
                pass
