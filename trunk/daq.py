# This file is part of muonic, a program to work with the QuarkDAQ cards
# Copyright (C) 2009  Robert Franke (robert.franke@desy.de)
#
# muonic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# muonic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with muonic. If not, see <http://www.gnu.org/licenses/>.


# The way of the communication between the serial port and the GUI is based on
# the receipt presented at http://code.activestate.com/recipes/82965/
# Created by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
# Adapted by Boudewijn Rempt, Netherlands. 2002-04-15
# It is licenced under the Python licence, http://www.python.org/psf/license/


import sys
import threading
import Queue

from PyQt4 import QtCore
from PyQt4 import QtGui

#from daq.DaqConnection import DaqConnection
from daq.SimDaqConnection import SimDaqConnection
from gui.MainWindow import MainWindow
from gui.live.scalarsmonitor import ScalarsWindow


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self):
        # Create the queue
        self.outqueue = Queue.Queue()
        self.inqueue = Queue.Queue()
        self.running = 1

        # another queue for the scalars
        self.outqueue_s = Queue.Queue(maxsize=1)
        self.inqueue_s = Queue.Queue()
 
        # Set up the GUI part
        self.gui=MainWindow(self.outqueue, self.inqueue, self.endApplication)
        self.gui.show()
        self.scalarswindow = ScalarsWindow(self.outqueue_s, self.inqueue_s)
        self.scalarswindow.show()


        # A timer to periodically call periodicCall :-)
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.periodicCall)

        # Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(100)

        self.daq = SimDaqConnection(self.inqueue, self.outqueue)
        self.daq_s = SimDaqConnection(self.inqueue_s,self.outqueue_s)
        
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.readthread = threading.Thread(target=self.daq.read)
        self.writethread = threading.Thread(target=self.daq.write)
        
        self.readthread_s = threading.Thread(target=self.daq_s.read)
        self.writethread_s = threading.Thread(target=self.daq_s.write)
        # Set daemon flag so that the threads finish when the main app finishes
        self.readthread.daemon = True
        self.writethread.daemon = True
        self.readthread.start()
        self.writethread.start()
        
        self.readthread_s.daemon = True
        self.writethread_s.daemon = True
        self.readthread_s.start()
        self.writethread_s.start()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            self.daq.running = False
            root.quit()

    def endApplication(self):
        self.running = False

def main():
    root = QtGui.QApplication(sys.argv)
    client = ThreadedClient()
    root.exec_()

if __name__ == '__main__':
    main()

# vim: ai ts=4 sts=4 et sw=4
