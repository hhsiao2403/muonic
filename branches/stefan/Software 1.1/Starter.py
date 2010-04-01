import sys
from PyQt4 import QtCore, QtGui
from threading import Thread
import Queue


from VerbindungDAQ import DaqConnection
from Hauptfenster import Ui_Hauptfenster,  Hauptfenster

class Hauptablaufprogramm():

    def __init__(self):
        #Thread.__init__(self)
        self.outqueue = Queue.Queue()
        self.inqueue = Queue.Queue()   
        self.running = 1   
        self.hauptfenster = Hauptfenster()
        self.hauptfenster.show()
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.periodicCall)
        self.timer.start(100)
        self.daq = DaqConnection(self.inqueue, self.outqueue)
        self.readthread = Thread(target=self.daq.read)
        self.writethread = Thread(target=self.daq.write)
        self.readthread.daemon = True
        self.writethread.daemon = True
        self.readthread.start()
        self.writethread.start()

    def periodicCall(self):
        self.processIncoming()
        if not self.running:
            self.daq.running = False
            root.quit()
        
    def endApplication(self):
        self.running = False
        
    def processIncoming(self):
        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                self.hauptfenster.plainTextEdit.appendPlainText(str(msg))
                if self.write_file:
                    self.outputfile.write(str(msg)+'\n')
            except Queue.Empty:
                pass
    
root = QtGui.QApplication(sys.argv)
client = Hauptablaufprogramm()
root.exec_()

