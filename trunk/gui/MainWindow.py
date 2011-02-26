from PyQt4 import QtGui
from PyQt4 import QtCore

import Queue

from gui.LineEdit import LineEdit
from gui.PeriodicCallDialog import PeriodicCallDialog
from gui.ThresholdDialog import ThresholdDialog
from gui.HelpWindow import HelpWindow
from gui.live.ScalarsWindow import ScalarsWindow
#from gui.live.scalarsmonitor import ScalarsWindow as ScalarsWindow2
from gui.live.scalarsmonitor import ScalarsMonitor
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import os

tr = QtCore.QCoreApplication.translate
_NAME = 'muonic'



class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        #self.resize(640, 480)
        self.resize(800, 600)
        self.setWindowTitle(_NAME)
        self.statusBar().showMessage(tr('MainWindow','Ready'))
         
        # scalars  
        self.previous_time = 2 
        self.scalars_result = (0,0,0,0,0)
        self.scalars_ch0 = 0 
        self.scalars_ch1 = 0
        self.scalars_ch2 = 0
        self.scalars_ch3 = 0
        self.scalars_trigger = 0
        self.scalars_time = 1
 
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.endcommand = endcommand

        self.create_widgets()

    def create_widgets(self):
        
        
        self.subwindow = SubWindow(self)       
        self.setCentralWidget(self.subwindow)

        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip(tr('MainWindow','Set trigger thresholds'))
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)
        scalars = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'Scalars', self)
        self.connect(scalars, QtCore.SIGNAL('triggered()'), self.scalars_menu)
        menubar = self.menuBar()
        file = menubar.addMenu(tr('MainWindow','&File'))
        file.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(thresholds)
        help = menubar.addMenu(tr('MainWindow','&Help'))
        help.addAction(helpdaqcommands)
        liveanalysis = menubar.addMenu(tr('MainWindow','&Live Analysis'))
        liveanalysis.addAction(scalars)

        toolbar = self.addToolBar(tr('MainWindow','Exit'))
        toolbar.addAction(exit)

    #the individual menus
    def threshold_menu(self):
        threshold_window = ThresholdDialog()
        rv = threshold_window.exec_()
        if rv == 1:
            # Here we should set the thresholds
            thresh_ch0 = int(threshold_window.ch0_input.text())
            thresh_ch1 = int(threshold_window.ch1_input.text())
            thresh_ch2 = int(threshold_window.ch2_input.text())
            thresh_ch3 = int(threshold_window.ch3_input.text())
            self.outqueue.put('TL 0 ' + str(thresh_ch0))
            self.outqueue.put('TL 1 ' + str(thresh_ch1))
            self.outqueue.put('TL 2 ' + str(thresh_ch2))
            self.outqueue.put('TL 3 ' + str(thresh_ch3))
   
    def help_menu(self):
        help_window = HelpWindow()
        #rv = threshold_window.exec_()
        help_window.exec_()
        #tr.exec_()	

    def scalars_menu(self):
        
        scalars_window = ScalarsWindow(self.scalars)
        rv = scalars_window.exec_()
        #if rv == 1:
            #while True:
                #scalars_window.scalars = self.scalars
                #pass

    #this functions gets everything out of the inqueue
    #All calculations should happen here
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        

        while self.inqueue.qsize():

            try:
                msg = self.inqueue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.subwindow.text_box.appendPlainText(str(msg))
                if self.subwindow.write_file:
                    self.subwindow.outputfile.write(str(msg)+'\n')

                # check for scalar information
                if msg[0]=='D' and msg[1] == 'S':
                    if len(msg) > 5:
                         self.scalars = msg
                         self.scalars = self.scalars.split()
                         print self.scalars, 'self.scalars'

                         for item in self.scalars:
    
                             if ("SO" in item) & (len(item) == 11):
                                 self.scalars_ch0 = int(item[3:],16)
                             if ("S1" in item) & (len(item) == 11):
                                 self.scalars_ch1 = int(item[3:],16)
                             if ("S2" in item) & (len(item) == 11):
                                 self.scalars_ch2 = int(item[3:],16)
                             if ("S3" in item) & (len(item) == 11):
                                 self.scalars_ch3 = int(item[3:],16)
                             if ("S4" in item) & (len(item) == 11):
                                 self.scalars_trigger = int(item[3:],16)
                             if ("S5" in item) & (len(item) == 11):
                                 self.scalars_time = int(item[3:],16)
                                
                         if self.scalars_time > self.previous_time:
                             time_window = self.scalars_time - self.previous_time
                             self.previous_time = self.scalars_time

                         else:
                             time_window = self.scalars_time
                         
                         if not time_window:
                             time_window=10
                         #send the counted scalars to the subwindow
                         self.subwindow.scalars_result = (self.scalars_ch0/time_window,self.scalars_ch1/time_window,self.scalars_ch2/time_window,self.scalars_ch3/time_window,self.scalars_trigger/time_window,self.scalars_time)
            except Queue.Empty:
                pass
   
    def closeEvent(self, ev):
        """
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        if self.subwindow.write_file:
            self.subwindow.outputfile.close()
        self.endcommand()


class SubWindow(QtGui.QWidget):
    def __init__(self,mainwindow):
        QtGui.QWidget.__init__(self)
       
        self.mainwindow = mainwindow
        self.setGeometry(0,0, 500,650)
        self.setWindowTitle("Debreate")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.resize(500,650)
        self.setMinimumSize(500,650)
        self.center()
        self.write_file = False
        self.scalars_result = (0,0,0,0,0)




        self.label = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit = LineEdit()
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


        #create the several tabs 
        tab_widget = QtGui.QTabWidget()
        tab1 = QtGui.QWidget()
        tab2 = QtGui.QWidget()
        
        p1_vertical = QtGui.QVBoxLayout(tab1)
        p2_vertical = QtGui.QVBoxLayout(tab2)
        
        tab_widget.addTab(tab1, "DAQ output")
        tab_widget.addTab(tab2, "Scalars")
        
        p1_vertical.addWidget(self.text_box)
        second_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        h_box.addWidget(self.file_button)
        h_box.addWidget(self.periodic_button)
        second_widget.setLayout(h_box)
        p1_vertical.addWidget(second_widget)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(tab_widget)
        
        self.setLayout(vbox)
        
        self.scalars_monitor = ScalarsMonitor(self)
        self.timerEvent(None)
        self.timer = self.startTimer(5000)

        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.scalars_monitor, self)
        # pack these widget into the vertical box
        p2_vertical.addWidget(self.scalars_monitor)
        p2_vertical.addWidget(ntb)
              

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def on_hello_clicked(self):
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.outqueue.put(str(self.hello_edit.displayText()))
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
        periodic_window = PeriodicCallDialog()
        rv = periodic_window.exec_()
        if rv == 1:
            period = periodic_window.time_box.value() * 1000 #We need the period in milliseconds
            command = str(periodic_window.textbox.text())
            commands = command.split('+')
            def periodic_put():
                for c in commands:
                    self.mainwindow.outqueue.put(c)
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

    def timerEvent(self,ev):
        """Custom timerEvent code, called at timer event receive"""
        #get the scalar information from the card
        self.mainwindow.outqueue.put('DS')
        self.mainwindow.outqueue.task_done()

        #self.scalars_result will always be up to date by MainWindow.ProcessIncoming()
        result = self.scalars_result
        # append new data to the datasets
        self.scalars_monitor.chan0.append(result[0])
        self.scalars_monitor.chan1.append(result[1])
        self.scalars_monitor.chan2.append(result[2])
        self.scalars_monitor.chan3.append(result[3])
        self.scalars_monitor.trigger.append(result[4])
        # update lines data using the lists with new data
        self.scalars_monitor.l_chan0.set_data(range(len(self.scalars_monitor.chan0)), self.scalars_monitor.chan0)
        self.scalars_monitor.l_chan1.set_data(range(len(self.scalars_monitor.chan1)), self.scalars_monitor.chan1)
        self.scalars_monitor.l_chan2.set_data( range(len(self.scalars_monitor.chan2)), self.scalars_monitor.chan2)
        self.scalars_monitor.l_chan3.set_data(range(len(self.scalars_monitor.chan3)), self.scalars_monitor.chan3)
        self.scalars_monitor.l_trigger.set_data(range(len(self.scalars_monitor.trigger)), self.scalars_monitor.trigger)
        

        #self.scalars_monitor.ax.set_xlim(0, 30)
        ma = max( max(self.scalars_monitor.chan0), max(self.scalars_monitor.chan1), max(self.scalars_monitor.chan2), 
                  max(self.scalars_monitor.chan3), max(self.scalars_monitor.trigger)  )
        self.scalars_monitor.ax.set_ylim(-1, ma*1.01)
        self.scalars_monitor.ax.set_xlim(-1, len(self.scalars_monitor.chan0))
        # force a redraw of the Figure
        self.scalars_monitor.fig.canvas.draw()
        # if we've done all the iterations
        if self.scalars_monitor.cnt == self.scalars_monitor.MAXITERS:
            # stop the timer
            self.killTimer(self.timer)
        else:
            # else, we increment the counter
            self.scalars_monitor.cnt += 1

# vim: ai ts=4 sts=4 et sw=4
