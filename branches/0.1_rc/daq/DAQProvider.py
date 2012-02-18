
import multiprocessing as mult

from gui.MainWindow import MainWindow

# PyQt4 imports
from PyQt4 import QtCore
from PyQt4 import QtGui

from SimDaqConnection import SimDaqConnection
from DaqConnection import DaqConnection


class DAQProvider():
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """

    def __init__(self,opts,logger,root):


        self.outqueue = mult.Queue()
        self.inqueue  = mult.Queue()
            
        self.running = 1
        self.root = root

        # get option parser options
        self.logger = logger
        self.sim = opts.sim

        # Set up the GUI part
        self.gui=MainWindow(self.outqueue, self.inqueue, self.endApplication, logger, opts) 
        self.gui.show()

        # A timer to periodically call periodicCall :-)
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.periodicCall)

        # Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(1000)

        if self.sim:
            self.daq = SimDaqConnection(self.inqueue, self.outqueue, self.logger)

        else:
            self.daq = DaqConnection(self.inqueue, self.outqueue, self.logger)
        
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        # Set daemon flag so that the threads finish when the main app finishes
        self.readthread = mult.Process(target=self.daq.read,name="pREADER")
        self.readthread.daemon = True
        self.readthread.start()
        if not self.sim:
            self.writethread = mult.Process(target=self.daq.write,name="pWRITER")
            self.writethread.daemon = True
            self.writethread.start()
        
        

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            self.daq.running = False
            try:
                self.gui.mu_file.close()

            except AttributeError:
                pass

            self.root.quit()

    def endApplication(self):
        self.gui.subwindow.writefile = False
        try:
            self.gui.mu_file.close()

        except AttributeError:
            pass

        self.running = False
        self.root.quit()       
 

