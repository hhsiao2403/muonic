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
import time
import threading
import Queue
import os
import gzip

from PyQt4 import QtGui
from PyQt4 import QtCore
import serial

_NAME = 'muonic'
tr = QtCore.QCoreApplication.translate

class MyPeriodicDialog(QtGui.QDialog):

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
    

class MyLineEdit(QtGui.QLineEdit):

    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        self.history=[]
        self.hist_pointer = 0
        
    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key()==QtCore.Qt.Key_Down:
                self.emit(QtCore.SIGNAL("keyDownPressed"))
                if self.hist_pointer < len(self.history)-1:
                    self.hist_pointer += 1
                    self.setText(self.history[self.hist_pointer])
                elif self.hist_pointer == len(self.history)-1:
                    self.setText('')
                    self.hist_pointer += 1
                return True
            if event.key()==QtCore.Qt.Key_Up:
                self.emit(QtCore.SIGNAL("keyUpPressed"))
                if self.hist_pointer > 0:
                    self.hist_pointer -= 1
                    self.setText(self.history[self.hist_pointer])
                return True
            else:
                return QtGui.QLineEdit.event(self, event)
        return QtGui.QLineEdit.event(self, event)

    def add_hist_item(self,item):
        self.history.append(item)
        self.hist_pointer = len(self.history)


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        self.resize(640, 480)
        self.setWindowTitle(_NAME)
        self.statusBar().showMessage(tr('MainWindow','Ready'))
        
        self.write_file = False
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.endcommand = endcommand
        self.create_widgets()

    def create_widgets(self):
        self.label = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit = MyLineEdit()
        self.hello_button = QtGui.QPushButton(tr('MainWindow','Send'))
        self.file_button = QtGui.QPushButton(tr('MainWindow', 'Save to File'))
        self.periodic_button = QtGui.QPushButton(tr('MainWindow', 'Periodic Call'))

        QtCore.QObject.connect(self.hello_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_hello_clicked
                              )
        QtCore.QObject.connect(self.hello_edit,
                              QtCore.SIGNAL("returnPressed()"),
                              self.on_hello_clicked
                              )
        
        QtCore.QObject.connect(self.file_button,
                                QtCore.SIGNAL("clicked()"),
                                self.on_file_clicked
                                )
        QtCore.QObject.connect(self.periodic_button,
                                QtCore.SIGNAL("clicked()"),
                                self.on_periodic_clicked
                                )

        self.text_box = QtGui.QPlainTextEdit()
        self.text_box.setReadOnly(True)
        # only 500 lines history
        self.text_box.document().setMaximumBlockCount(500)
        v_box = QtGui.QVBoxLayout()
        v_box.addWidget(self.text_box)
        second_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        h_box.addWidget(self.file_button)
        h_box.addWidget(self.periodic_button)
        second_widget.setLayout(h_box)
        v_box.addWidget(second_widget)
        central_widget = QtGui.QWidget()
        central_widget.setLayout(v_box)
        self.setCentralWidget(central_widget)
        
        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        menubar = self.menuBar()
        file = menubar.addMenu(tr('MainWindow','&File'))
        file.addAction(exit)

        toolbar = self.addToolBar(tr('MainWindow','Exit'))
        toolbar.addAction(exit)

    def on_hello_clicked(self):
#        QtGui.QMessageBox.information(self,
#                                     "Hello",
#                                     "Hello %s"%self.hello_edit.displayText(),
#                                     QtGui.QMessageBox.Ok)
#        self.text_box.append(self.hello_edit.displayText())
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.outqueue.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                tr('MainWindow','Open output file'),
                                os.getenv('HOME'), tr('MainWindow','Text Files (*.txt);;All Files (*)'));
        filename = str(filename)
        if len(filename) > 0:
            if filename.endswith('.gz'):
                self.outputfile = gzip.open(filename,'w')
            else:
                self.outputfile = open(filename,'w')
            self.write_file = True
            self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%filename))
            self.statusBar().addPermanentWidget(self.file_label)


    def on_periodic_clicked(self):
        periodic_window = MyPeriodicDialog()
        rv = periodic_window.exec_()
        if rv == 1:
            period = periodic_window.time_box.value() * 1000 #We need the period in milliseconds
            command = str(periodic_window.textbox.text())
            commands = command.split('+')
            def periodic_put():
                for c in commands:
                    self.outqueue.put(c)
            self.periodic_put = periodic_put
            self.timer = QtCore.QTimer()
            QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.periodic_put)
            self.periodic_put()
            self.timer.start(period)
            self.periodic_status_label = QtGui.QLabel(tr('MainWindow','%s every %s sec'%(command,period/1000)))
            self.statusBar().addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.timer.stop()
                self.statusBar().removeWidget(self.periodic_status_label)
            except AttributeError:
                pass

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.text_box.appendPlainText(str(msg))
                if self.write_file:
                    self.outputfile.write(str(msg)+'\n')
            except Queue.Empty:
                pass
    
    def closeEvent(self, ev):
        """
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        if self.write_file:
            self.outputfile.close()
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
        self.gui=MainWindow(self.outqueue, self.inqueue, self.endApplication)
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
client = ThreadedClient()
root.exec_()
