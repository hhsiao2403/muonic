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
from gui.live.lifetimemonitor import LifetimeMonitor
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import os
import numpy as n
import time

import gc
gc.set_threshold(1000000)

reso_w = 600
reso_h = 400


tr = QtCore.QCoreApplication.translate
_NAME = 'muonic'

#define some global variables to calculate the rates
SCALARS_LAST_TIME = time.time() #Return the current time in seconds since the Epoch


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, filename, debug, timewindow, win_parent = None):
        self.debug = debug
        self.filename = filename             
        self.timewindow = timewindow

        if self.debug: print "Welcome to MainWindow!"
        
        
        QtGui.QMainWindow.__init__(self, win_parent)
        self.resize(reso_w, reso_h)
        self.setWindowTitle(_NAME)
        self.statusBar().showMessage(tr('MainWindow','Ready'))      

        # scalars 
        self.readout_scalars = False
        self.scalars_ch0_previous = 0
        self.scalars_ch1_previous = 0
        self.scalars_ch2_previous = 0
        self.scalars_ch3_previous = 0
        self.scalars_trigger_previous = 0
        self.scalars_time = 0
        
        self.data_file = open('data.txt', 'w')
        self.data_file.write('time | chan0 | chan1 | chan2 | chan3 | R0 | R1 | R2 | R3 | trigger | Delta_time \n')
 
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.endcommand = endcommand

        self.create_widgets()


    def create_widgets(self):       
       
        print "Uebergabe debug", self.debug
        self.subwindow = SubWindow(self, self.timewindow, self.debug)       
        self.setCentralWidget(self.subwindow)

        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))
        #self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.connect(exit, QtCore.SIGNAL('triggered()'), self.exit_program)
        self.connect(self, QtCore.SIGNAL('closeEmitApp()'), QtCore.SLOT('close()') )
        ##self.connect(self.okButton, QtCore.SIGNAL("clicked()"),
        ##             self, QtCore.SLOT("accept()"))
        ##self.connect(self.cancelButton, QtCore.SIGNAL("clicked()"),
        ##             self, QtCore.SLOT("reject()"))

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


    def verification(self, question_string):
        reply = QtGui.QMessageBox.question(self, 'Message',
                question_string, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False


    def exit_program(self):
        # exit the main program after verification
        #q = Verification()
        #q.show()
        if self.verification('Do you really want to exit?'):
            print 'Exit!'
            self.emit(QtCore.SIGNAL('closeEmitApp()'))
            
        #q.exec_()


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
            #self.outqueue.task_done() 
    def help_menu(self):
        help_window = HelpWindow()
        #rv = threshold_window.exec_()
        help_window.exec_()
        #tr.exec_()	

    def scalars_menu(self):
        
        scalars_window = ScalarsWindow(self.scalars)
        rv = scalars_window.exec_()

    #this functions gets everything out of the inqueue
    #All calculations should happen here
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        
        if self.debug: print  "PROCESS INCOMING: length of inqueue: ", self.    inqueue.qsize()
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

                         if not self.readout_scalars:
                             self.readout_scalars = True
                             break
                         
                         self.scalars = msg
                         self.scalars = self.scalars.split()
                         #make a time window and reset SCALARS_LAST_TIME
                         global SCALARS_LAST_TIME
                         time_window = time.time() - SCALARS_LAST_TIME 
                         SCALARS_LAST_TIME = time.time()
                         #print time_window, 'time window'

                         for item in self.scalars:
                             if ("S0" in item) & (len(item) == 11):
                                 self.scalars_ch0 = int(item[3:],16)
                             elif ("S1" in item) & (len(item) == 11):
                                 self.scalars_ch1 = int(item[3:],16)
                             elif ("S2" in item) & (len(item) == 11):
                                 self.scalars_ch2 = int(item[3:],16)
                             elif ("S3" in item) & (len(item) == 11):
                                 self.scalars_ch3 = int(item[3:],16)
                             elif ("S4" in item) & (len(item) == 11):
                                 self.scalars_trigger = int(item[3:],16)
                             elif ("S5" in item) & (len(item) == 11):
                                 self.scalars_time = float(int(item[3:],16))
                             else:
                                 #print 'PROCESS INCOMING: unknown item detected!',item
                                 pass

                         self.scalars_diff_ch0 = self.scalars_ch0 - self.scalars_ch0_previous 
                         self.scalars_diff_ch1 = self.scalars_ch1 - self.scalars_ch1_previous 
                         self.scalars_diff_ch2 = self.scalars_ch2 - self.scalars_ch2_previous 
                         self.scalars_diff_ch3 = self.scalars_ch3 - self.scalars_ch3_previous 
                         self.scalars_diff_trigger = self.scalars_trigger - self.scalars_trigger_previous 

                         #cut off the plot, set maximum rate to 35 Hz
# if self.scalars_diff_ch0 > 35:
#     self.scalars_diff_ch0 = 35
# if self.scalars_diff_ch1 > 35:
#     self.scalars_diff_ch1 = 35
# if self.scalars_diff_ch2 > 35:
#     self.scalars_diff_ch2 = 35
# if self.scalars_diff_ch3 > 35:
#     self.scalars_diff_ch3 = 35
# #the triggerrate can be larger    
# if self.scalars_diff_trigger > 60:
#     self.scalars_diff_trigger = 60
# 
                         self.scalars_ch0_previous = self.scalars_ch0
                         self.scalars_ch1_previous = self.scalars_ch1
                         self.scalars_ch2_previous = self.scalars_ch2
                         self.scalars_ch3_previous = self.scalars_ch3
                         self.scalars_trigger_previous = self.scalars_trigger
                         #if the time window is too small
                         #this can cause an unphysical 
                         #high rate
                         if time_window < 0.5:
                             print 'PROCESS INCOMING: WARN: time window to small, setting time_window = 0.5'
                             time_window = 0.5
                         
                         #send the counted scalars to the subwindow
                         scalars_result = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window)
                         self.subwindow.scalars_monitor.update_plot(scalars_result)
                         #write the rates to data file
                         self.data_file.write('%f %f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_time, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                         
            except Queue.Empty:
                pass
   
    def closeEvent(self, ev):
        """
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        if self.subwindow.write_file:
            self.subwindow.outputfile.close()
        self.data_file.close()
        self.endcommand()


class SubWindow(QtGui.QWidget):
    def __init__(self, mainwindow, timewindow, debug):
        QtGui.QWidget.__init__(self)
        
        self.timewindow = timewindow
        self.debug = debug
        self.mainwindow = mainwindow
        self.setGeometry(0,0, reso_w,reso_h)
        self.setWindowTitle("Debreate")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.resize(reso_w,reso_h)
        self.setMinimumSize(reso_w,reso_h)
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
        tab3 = QtGui.QWidget()

        p1_vertical = QtGui.QVBoxLayout(tab1)
        p2_vertical = QtGui.QVBoxLayout(tab2)
        p3_vertical = QtGui.QVBoxLayout(tab3)

        tab_widget.addTab(tab1, "DAQ output")
        tab_widget.addTab(tab2, "Rates")
        tab_widget.addTab(tab3, "Lifetime")
        
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
        
        self.scalars_monitor = ScalarsMonitor(self, self.timewindow, debug)
        self.lifetime_monitor = LifetimeMonitor(self)
        self.timerEvent(None)
        self.timer = self.startTimer(self.timewindow*1000)

        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.scalars_monitor, self)
        # pack these widget into the vertical box
        p2_vertical.addWidget(self.scalars_monitor)
        p2_vertical.addWidget(ntb)

        ntb = NavigationToolbar(self.lifetime_monitor, self)
        # pack these widget into the vertical box
        p3_vertical.addWidget(self.lifetime_monitor)
        p3_vertical.addWidget(ntb)

             

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def on_hello_clicked(self):
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.outqueue.put(str(self.hello_edit.displayText()))
            #self.outqueue.task_done()
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
                    #self.mainwindow.outqueue.task_done()
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
        #self.mainwindow.outqueue.task_done()
        if self.debug: print "GC:", len(gc.get_objects()), "objects traced by gc"
        not_reachable = gc.collect()
        if self.debug: print "GC: All objects collected!"
        if self.debug: print "GC:", not_reachable, "objects were not reachable!"
        if self.debug: print "GC:", len(gc.get_objects()), "objects traced by gc"

        #make lifetime histogram
        mu, sigma = 100, 15
        x = mu + sigma*n.random.randn(10000)
        #i = len(self.scalars_monitor.chan0)
        #self.lifetime_monitor.lifetime.append(x[i])
        #print "x[i] = ", x[i]
        #print self.lifetime_monitor.lifetime
        #self.lifetime_monitor.update_plot(self.lifetime_monitor.lifetime)
        #self.lifetime_monitor.ax.clear()
        #self.lifetime_monitor.lifetime_plot = self.lifetime_monitor.ax.hist(self.lifetime_monitor.lifetime, 20, facecolor='blue')
        #self.lifetime_monitor.fig.canvas.draw()
        

        
        #self.scalars_monitor.update_plot()

        # if we've done all the iterations
        #if self.scalars_monitor.cnt == self.scalars_monitor.MAXITERS:
        #    # stop the timer
        #    self.killTimer(self.timer)
        #else:
        #    # else, we increment the counter
        #    self.scalars_monitor.cnt += 1

# vim: ai ts=4 sts=4 et sw=4
