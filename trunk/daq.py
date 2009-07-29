# This file is part of FermiDAQ, a program to work with the QuarkDAQ cards
# Copyright (C) 2009  Robert Franke (robert.franke@desy.de)
#
# FermiDAQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# FermiDAQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with FermiDAQ.  If not, see <http://www.gnu.org/licenses/>.


# The way of the communication between the serial port and the GUI is based on
# the receipt presented at http://code.activestate.com/recipes/82965/
# Created by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
# Adapted by Boudewijn Rempt, Netherlands. 2002-04-15
# It is licenced under the Python licence, http://www.python.org/psf/license/


import sys, time, threading, Queue
from PyQt4 import QtGui
from PyQt4 import QtCore
import serial

class HelloWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.endcommand = endcommand
        self.create_widgets()

    def create_widgets(self):
        self.label = QtGui.QLabel("Say hello")
        self.hello_edit = QtGui.QLineEdit()
        self.hello_button = QtGui.QPushButton("Push Me!")

        QtCore.QObject.connect(self.hello_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_hello_clicked
                              )
        QtCore.QObject.connect(self.hello_edit,
                              QtCore.SIGNAL("returnPressed()"),
                              self.on_hello_clicked
                              )

        self.text_box = QtGui.QTextEdit()
        self.text_box.setReadOnly(True)
        v_box = QtGui.QVBoxLayout()
        v_box.addWidget(self.text_box)
        second_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        second_widget.setLayout(h_box)
        v_box.addWidget(second_widget)
        central_widget = QtGui.QWidget()
        central_widget.setLayout(v_box)
        self.setCentralWidget(central_widget)

    def on_hello_clicked(self):
#        QtGui.QMessageBox.information(self,
#                                     "Hello",
#                                     "Hello %s"%self.hello_edit.displayText(),
#                                     QtGui.QMessageBox.Ok)
#        self.text_box.append(self.hello_edit.displayText())
        self.outqueue.put(str(self.hello_edit.displayText()))
        self.hello_edit.clear()

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.text_box.append(str(msg))
            except Queue.Empty:
                pass
    
    def closeEvent(self, ev):
        """
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        self.endcommand()


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self):
        # Create the queue
        self.outqueue = Queue.Queue()
        self.inqueue = Queue.Queue()

        # Set up the GUI part
        self.gui=HelloWindow(self.outqueue, self.inqueue, self.endApplication)
        self.gui.show()

        # A timer to periodically call periodicCall :-)
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.periodicCall)
        try:
            self.port = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,parity='N',stopbits=1,timeout=1,xonxoff=True)
        except serial.SerialException, e:
            print e.message
            sys.exit(1)

        # Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(100)

        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread2 = threading.Thread(target=self.workerThread2)
        self.thread1.start()
        self.thread2.start()


    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            root.quit()

    def endApplication(self):
        self.running = 0

    
    def workerThread2(self):
        while self.running:
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    pass
            time.sleep(0.1)


    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        min_sleeptime = 0.01 # seconds
        max_sleeptime = 0.2 # seconds
        sleeptime = min_sleeptime #seconds
        while self.running:
            if self.port.inWaiting():
                while self.port.inWaiting():
                    self.outqueue.put(self.port.readline().strip())
                sleeptime = max(sleeptime/2, min_sleeptime)
            else:
                sleeptime = min(1.5 * sleeptime, max_sleeptime)
            time.sleep(sleeptime)


root = QtGui.QApplication(sys.argv)
def periodicCall():
    print "Hello"

client = ThreadedClient()
root.exec_()
