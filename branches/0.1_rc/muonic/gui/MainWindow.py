#! /usr/bin/env python

"""
Provides the main window for the gui part of muonic
"""

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

# multithreading imports
import Queue

# muonic imports
from LineEdit import LineEdit
from PeriodicCallDialog import PeriodicCallDialog
from ThresholdDialog import ThresholdDialog
from ConfigDialog import ConfigDialog
from OptionsDialog import OptionsDialog
from HelpWindow import HelpWindow
from muonic.gui.live.scalarsmonitor import ScalarsMonitor
from muonic.gui.live.lifetimemonitor import LifetimeMonitor
from muonic.gui.live.pulsemonitor import PulseMonitor

from muonic.analysis import fit

import PulseAnalyzer as pa
import get_time

from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time


reso_w = 600
reso_h = 400

tr = QtCore.QCoreApplication.translate
_NAME = 'muonic'

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, logger, opts, root, win_parent = None):

        # instanciate the mainwindow
        self.logger = logger
        self.options = MuonicOptions(float(opts.timewindow),opts.writepulses,opts.nostatus,opts.user)
        self.ini = True  # is it the first time all the functions are called?
        self.mu_ini = True # is it the first time thet the mudecaymode is started?        

        # this holds the scalars in the time interval
        self.channel_counts = [0,0,0,0,0] #[trigger,ch0,ch1,ch2,ch3]

        # keep the last decays
        self.decay = []

        # last time, when the 'DS' command was sent
        self.lastscalarquery = time.time()
        self.thisscalarquery = time.time()
        self.lastoneppscount = 0
              
        # the current thresholds
        self.threshold_ch0 = 'n.a.'
        self.threshold_ch1 = 'n.a.'
        self.threshold_ch2 = 'n.a.'
        self.threshold_ch3 = 'n.a.'


        # the pulseextractor for direct analysis
        self.pulseextractor = pa.PulseExtractor(pulsefile=self.options.pulsefilename) 
        self.pulses = ()


        # initialize MainWindow gui
        QtGui.QMainWindow.__init__(self, win_parent)
        self.resize(reso_w, reso_h)
        self.setWindowTitle(_NAME)
        self.statusbar = QtGui.QMainWindow.statusBar(self)
        self.statusbar.showMessage(tr('MainWindow','Ready'))      

        # prepare fields for scalars 
        self.readout_scalars = False
        self.scalars_ch0_previous = 0
        self.scalars_ch1_previous = 0
        self.scalars_ch2_previous = 0
        self.scalars_ch3_previous = 0
        self.scalars_trigger_previous = 0
        self.scalars_time = 0
        
        self.data_file = open(self.options.filename, 'w')
        self.data_file.write('time | chan0 | chan1 | chan2 | chan3 | R0 | R1 | R2 | R3 | trigger | Delta_time \n')
        
        # always write the rate plot data
        self.data_file_write = True

        self.inqueue = inqueue
        self.outqueue = outqueue

        # we have to ensure that the DAQcard does not sent
        # any automatic status reports every x seconds
        self.outqueue.put('ST N!=1')
        self.outqueue.put('ST 0')
        self.outqueue.put('TL')

        # an anchor to the Application
        self.root = root

        # A timer to periodically call processIncoming and check what is in the queue
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.processIncoming)
 
        ## Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(1000)



        self.create_widgets()


    def create_widgets(self):       
       
        self.subwindow = SubWindow(self, self.options.timewindow, self.logger)       
        self.setCentralWidget(self.subwindow)

        # provide buttons to exit the application
        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))

        self.connect(exit, QtCore.SIGNAL('triggered()'), self.exit_program)
        self.connect(self, QtCore.SIGNAL('closeEmitApp()'), QtCore.SLOT('close()') )

        # prepare the config menu
        config = QtGui.QAction(QtGui.QIcon(''),'Channel Configuration', self)
        config.setStatusTip(tr('MainWindow','Configuer the Coincidences and channels'))
        self.connect(config, QtCore.SIGNAL('triggered()'), self.config_menu)
       
        # prepare the threshold menu
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip(tr('MainWindow','Set trigger thresholds'))
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
               
        # the options menu
        options = QtGui.QAction(QtGui.QIcon(''),'Options', self)
        options.setStatusTip(tr('MainWindow','Set program options'))
        self.connect(options, QtCore.SIGNAL('triggered()'), self.options_menu)

        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)
        scalars = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'Scalars', self)
        #self.connect(clear, QtCore.SIGNAL('triggered()'), self.clear_function)

        # create the menubar and fill it with the submenus
       
        menubar = self.menuBar()
        filemenu = menubar.addMenu(tr('MainWindow','&File'))
        filemenu.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(config)
        settings.addAction(thresholds)
        settings.addAction(options)

        helpmenu = menubar.addMenu(tr('MainWindow','&Help'))
        helpmenu.addAction(helpdaqcommands)
 
    def exit_program(self,ev):
        """
        The event which triggered exit_program has to be passed as ev
        So that if the verification fails, exit_program can catch it!
        """

        # ask kindly if the user is really sure if she/he wants to exit
        reply = QtGui.QMessageBox.question(self, 'Attention!',
                'Do you really want to exit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            now = datetime.datetime.now()

            # close the RAW file (if any)
            if self.subwindow.write_file:
                self.subwindow.write_file = False
                mtime = now - self.options.raw_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The raw data was written for %f hours" % mtime)
                newrawfilename = self.options.rawfilename.replace("HOURS",str(mtime))
                shutil.move(self.options.rawfilename,newrawfilename)
                self.subwindow.outputfile.close()

            if self.options.mudecaymode:

                self.options.mudecaymode = False
                mtime = now - self.options.dec_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The muon decay measurement was active for %f hours" % mtime)
                newmufilename = self.options.decayfilename.replace("HOURS",str(mtime))
                shutil.move(self.options.decayfilename,newmufilename)

            if self.options.pulsefilename:

                old_pulsefilename = self.options.pulsefilename

                # no pulses shall be extracted any more, 
                # this means changing lots of switches
                self.options.pulsefilename = False
                self.options.mudecaymode = False
                self.options.showpulses = False
                self.pulseextractor.close_file()
                mtime = now - self.options.pulse_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The pulse extraction measurement was active for %f hours" % mtime)
                newpulsefilename = old_pulsefilename.replace("HOURS",str(mtime))
                shutil.move(old_pulsefilename,newpulsefilename)

                

            self.data_file_write = False
            self.data_file.close()
            mtime = now - self.options.rate_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
            self.logger.info("The rate measurement was active for %f hours" % mtime)
            newratefilename = self.options.filename.replace("HOURS",str(mtime))
            shutil.move(self.options.filename,newratefilename)
            time.sleep(0.5)
            self.subwindow.writefile = False
            try:
                self.mu_file.close()
 
            except AttributeError:
                pass

            self.root.quit()           
            self.emit(QtCore.SIGNAL('closeEmitApp()'))

        else:
            ev.ignore()
    
    #the individual menus
    def threshold_menu(self):
        # get the actual Thresholds...
        self.outqueue.put('TL')

        threshold_window = ThresholdDialog(self.threshold_ch0,self.threshold_ch1,self.threshold_ch2,self.threshold_ch3)
        rv = threshold_window.exec_()
        if rv == 1:
            # Here we should set the thresholds

            # We have to check for integers!
            self.logger.debug("Type of input text is %s and its value is %s" %(type(threshold_window.ch0_input.text()),threshold_window.ch0_input.text()))

            try:
                int(threshold_window.ch0_input.text())
	        self.outqueue.put('TL 0 ' + threshold_window.ch0_input.text())

            except ValueError:
                self.logger.info("Can't convert to integer: field 0")
            try:
                int(threshold_window.ch1_input.text())
                self.outqueue.put('TL 1 ' + threshold_window.ch1_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 1")
            try:
                int(threshold_window.ch2_input.text())
                self.outqueue.put('TL 2 ' + threshold_window.ch2_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 2")
            try:
                int(threshold_window.ch3_input.text())
                self.outqueue.put('TL 3 ' + threshold_window.ch3_input.text())
            except ValueError:
                self.logger.info("Can't convert to integer: field 3")
	    

    def config_menu(self):
        config_window = ConfigDialog()
        rv = config_window.exec_()
        if rv == 1:
            
            chan0_active = config_window.activateChan0.isChecked() 
            chan1_active = config_window.activateChan1.isChecked() 
            chan2_active = config_window.activateChan2.isChecked() 
            chan3_active = config_window.activateChan3.isChecked() 
                        
            singles = config_window.coincidenceSingles.isChecked() 
            if singles:
                self.subwindow.scalars_monitor.do_not_show_trigger = True
            else:
                self.subwindow.scalars_monitor.do_not_show_trigger = False
            
            twofold = config_window.coincidenceTwofold.isChecked() 
            threefold = config_window.coincidenceThreefold.isChecked() 
            fourfold = config_window.coincidenceFourfold.isChecked() 

            noveto = config_window.noveto.isChecked()
            vetochan1 = config_window.vetochan1.isChecked()
            vetochan2 = config_window.vetochan2.isChecked()
            vetochan3 = config_window.vetochan3.isChecked()

            tmp_msg = ''
    
            for veto in [(noveto,'00'),(vetochan1,'01'),(vetochan2,'10'),(vetochan3,'11')]:
                if veto[0]:
                    tmp_msg += veto[1]
            
            if noveto:
                # ensure that there is no veto active and reset the 
                # temp message, just to be sure
                tmp_msg = '00'
    
            coincidence_set = False
            for coincidence in [(singles,'00'),(twofold,'01'),(threefold,'10'),(fourfold,'11')]:
                if coincidence[0]:
                    tmp_msg += coincidence[1]
                    coincidence_set = True
            
            # else case, just in case
            if not coincidence_set:
                tmp_msg += '00'
    
            # now calculate the correct expression for the first
            # four bits
            self.logger.debug("The first four bits are set to %s" %tmp_msg)
            msg = 'WC 00 ' + hex(int(''.join(tmp_msg),2))[-1].capitalize()
    
            channel_set = False
            enable = ['0','0','0','0']
            for channel in enumerate([chan3_active,chan2_active,chan1_active,chan0_active]):
                if channel[1]:
                    enable[channel[0]] = '1'
                    channel_set = True
            
            if not channel_set:
                msg += '0'
                
            else:
                msg += hex(int(''.join(enable),2))[-1].capitalize()
            
            self.outqueue.put(msg)
            self.logger.info('The following message was sent to DAQ: %s' %msg)
                    
    
            self.logger.debug('channel0 selected %s' %chan0_active)
            self.logger.debug('channel1 selected %s' %chan1_active)
            self.logger.debug('channel2 selected %s' %chan2_active)
            self.logger.debug('channel3 selected %s' %chan3_active)
            self.logger.debug('coincidence singles %s' %singles)
            self.logger.debug('coincidence twofold %s' %twofold)
            self.logger.debug('coincidence threefold %s' %threefold)
            self.logger.debug('coincidence fourfold %s' %fourfold)

    def options_menu(self):
        options_window = OptionsDialog()
        rv = options_window.exec_()
        if rv == 1:
            self.options.softveto = options_window.VetoCheckbox.isChecked()
            self.logger.info('Using Chan3 software veto %s' %self.options.softveto.__repr__())
            


    def help_menu(self):
        help_window = HelpWindow()
        help_window.exec_()

    def clear_function(self):
        self.logger.debug("Clear was called")
        self.subwindow.scalars_monitor.reset()

    # this functions gets everything out of the inqueue
    # All calculations should happen here
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        
        self.logger.debug("length of inqueue: %s" %self.inqueue.qsize())
        while self.inqueue.qsize():

            try:
                msg = self.inqueue.get(0)
                self.logger.debug("Got item from inqueue: %s" %msg.__repr__())

                # Check contents of message and do what it says
                # As a test, we simply print it
                self.subwindow.text_box.appendPlainText(str(msg))
                if self.subwindow.write_file:
                    try:
                        if self.options.nostatus:
                            fields = msg.rstrip("\n").split(" ")
                            if ((len(fields) == 16) and (len(fields[0]) == 8)):
                                self.subwindow.outputfile.write(str(msg)+'\n')
                            else:
                                self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
                        else:
                            self.subwindow.outputfile.write(str(msg)+'\n')

                    except ValueError:
			self.logger.info('Trying to write on closed file, captured!')


		# check for threshold information
                if msg.startswith('TL') and len(msg) > 3:
                    msg = msg.split('=')
                    self.threshold_ch0 = msg[1][:-2]
                    self.threshold_ch1 = msg[2][:-2]
                    self.threshold_ch2 = msg[3][:-2]
                    self.threshold_ch3 = msg[4]
                    

                # check for scalar information
                if len(msg) >= 2 and msg[0]=='D' and msg[1] == 'S':                    
                    #if len(msg) > 5 :
                        # This is necessary, that the first (unphysical)
                        # value is omitted from the calculation
                        # of the rates
                        if not self.readout_scalars:
                            self.readout_scalars = True
                            break
                         
                        self.scalars = msg.split()
                        time_window = self.thisscalarquery
                        self.logger.debug("Time window %s" %time_window)

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
                                self.logger.debug("unknown item detected: %s" %item.__repr__())

                        self.scalars_diff_ch0 = self.scalars_ch0 - self.scalars_ch0_previous 
                        self.scalars_diff_ch1 = self.scalars_ch1 - self.scalars_ch1_previous 
                        self.scalars_diff_ch2 = self.scalars_ch2 - self.scalars_ch2_previous 
                        self.scalars_diff_ch3 = self.scalars_ch3 - self.scalars_ch3_previous 
                        self.scalars_diff_trigger = self.scalars_trigger - self.scalars_trigger_previous 
                        
                        self.scalars_ch0_previous = self.scalars_ch0
                        self.scalars_ch1_previous = self.scalars_ch1
                        self.scalars_ch2_previous = self.scalars_ch2
                        self.scalars_ch3_previous = self.scalars_ch3
                        self.scalars_trigger_previous = self.scalars_trigger
                         
                        #send the counted scalars to the subwindow
                        self.subwindow.scalars_result = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_trigger)
                        #write the rates to data file
                        # we have to catch IOErrors, can occur if program is 
                        # exited
                        if self.data_file_write:
                            try:
                                self.data_file.write('%f %f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_time, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                                self.logger.debug("Rate plot data was written to %s" %self.data_file.__repr__())
                            except ValueError:
                                self.logger.warning("ValueError, Rate plot data was not written to %s" %self.data_file.__repr__())
                
                elif (self.options.mudecaymode or self.options.showpulses or self.options.pulsefilename) :
                    # we now assume that we are using chan0-2 for data taking anch chan3 as veto
                    self.pulses = self.pulseextractor.extract(msg)
                    
                    if (self.pulses != None):
                        # we have to count the triggers in the time intervall
                        self.channel_counts[0] += 1                         
                        for channel,pulses in enumerate(self.pulses[1:]):
                            if pulses:
                                for pulse in pulses:
                                    self.channel_counts[channel] += 1


                    # This can made simpler,
                    # if the DecayTrigger just looks for 
                    # two adjacent triggers,
                    # we do not neeed to
                    # run the pulseextractor.
                    # This needs some more programming, sort
                    # of implementing TriggerExtractor...
                    if self.options.mudecaymode:
                        if self.pulses != None:
                            if self.mu_ini:
                                self.dtrigger = pa.DecayTrigger(self.pulses,self.options.softveto)
                                self.mu_ini = False 
                                            
                            else:
                                tmpdecay = self.dtrigger.trigger(self.pulses)                   
                                if tmpdecay != None:
                                    when = time.asctime()
                                    self.decay.append((tmpdecay/100.,when))
                                    self.logger.info('We have found a decaying muon with a decaytime of %f at %s' %(tmpdecay,when)) 
                                    self.subwindow.muondecaycounter += 1
                                    self.subwindow.lastdecaytime = when

                                # cleanup
                                del tmpdecay

            except Queue.Empty:
                self.logger.debug("Queue empty!")
                pass
   
    def closeEvent(self, ev):
        """
        Is triggered when the window is closed, we have to reimplement it
        to provide our special needs for the case the program is ended.
        """

        self.logger.info('Attempting to close Window!')

        self.exit_program(ev)


class SubWindow(QtGui.QWidget):
    """
    The SubWindow will provide a tabbed interface.
    All functionality should be represented by tabs in the SubWindow
    """

    def __init__(self, mainwindow, timewindow, logger):

        QtGui.QWidget.__init__(self)
        
        self.mainwindow = mainwindow
        self.logger = logger
        self.logger.info("Timewindow is %4.2f" %timewindow)
        self.setGeometry(0,0, reso_w,reso_h)
        self.setWindowTitle("Debreate")
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.resize(reso_w,reso_h)
        self.setMinimumSize(reso_w,reso_h)
        self.center()
        self.write_file = False
        self.holdplot = False
        self.scalars_result = False 
        self.muondecaycounter = 0
        self.lastdecaytime = 'None'

        # provide the items which should go into the tabs
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
        tab4 = QtGui.QWidget()

        p1_vertical = QtGui.QVBoxLayout(tab1)
        p2_vertical = QtGui.QVBoxLayout(tab2)
        p3_vertical = QtGui.QVBoxLayout(tab3)
        p4_vertical = QtGui.QVBoxLayout(tab4)

        tab_widget.addTab(tab1, "DAQ output")
        tab_widget.addTab(tab2, "Muon Rates")
        tab_widget.addTab(tab3, "Muon Lifetime")
        tab_widget.addTab(tab4, "PulseAnalyzer")
        
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
       
        self.scalars_monitor = ScalarsMonitor(self, self.logger)
        self.lifetime_monitor = LifetimeMonitor(self,self.logger)
        self.pulse_monitor = PulseMonitor(self,self.logger)

        # buttons for restart/clear the plot     
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Restart'))
        self.stop_button = QtGui.QPushButton(tr('MainWindow', 'Stop'))

        # button for performing a mu lifetime fit
        self.mufit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!'))
        
        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )


        

        # pack theses widget into the vertical box
        p2_vertical.addWidget(self.scalars_monitor)
        #p2_vertical.addWidget(ntb)

        # instantiate the navigation toolbar
        p2_h_box = QtGui.QHBoxLayout()
        ntb = NavigationToolbar(self.scalars_monitor, self)
        p2_h_box.addWidget(ntb)
        p2_h_box.addWidget(self.start_button)
        p2_h_box.addWidget(self.stop_button)
        p2_second_widget = QtGui.QWidget()
        p2_second_widget.setLayout(p2_h_box)
        p2_vertical.addWidget(p2_second_widget)



        ntb2 = NavigationToolbar(self.lifetime_monitor, self)

        # now the mudecay tab..
        # activate Muondecay mode with a checkbox
        self.activateMuondecay = QtGui.QCheckBox(self)
        self.activateMuondecay.setText(tr("Dialog", "Check for decayed Muons \n- Warning! this will define your coincidence/Veto settings!", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activateMuondecay,
                              QtCore.SIGNAL("clicked()"),
                              self.activateMuondecayClicked
                              )

        self.displayMuons = QtGui.QLabel(self)
        self.lastDecay = QtGui.QLabel(self)
        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
 
        p3_vertical.addWidget(self.activateMuondecay)
        p3_vertical.addWidget(self.displayMuons)
        p3_vertical.addWidget(self.lastDecay)
        p3_vertical.addWidget(self.lifetime_monitor)

        p3_h_box = QtGui.QHBoxLayout()
        p3_h_box.addWidget(ntb2)
        p3_h_box.addWidget(self.mufit_button)
        p3_second_widget = QtGui.QWidget()
        p3_second_widget.setLayout(p3_h_box)
        p3_vertical.addWidget(p3_second_widget)

        ntb3 = NavigationToolbar(self.pulse_monitor, self)

        # the pulseanalyzer tab
        self.activatePulseanalyzer = QtGui.QCheckBox(self)
        self.activatePulseanalyzer.setText(tr("Dialog", "Show the last triggered pulses \n in the time interval", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.activatePulseanalyzer,
                              QtCore.SIGNAL("clicked()"),
                              self.activatePulseanalyzerClicked
                              )
        p4_vertical.addWidget(self.activatePulseanalyzer)
        p4_vertical.addWidget(self.pulse_monitor)
        p4_vertical.addWidget(ntb3)

        # start a timer which does something every timewindow seconds
        self.timerEvent(None)
        self.timer = self.startTimer(timewindow*1000)

    def startClicked(self): 
        self.logger.debug("Restart Button Clicked")
        self.holdplot = False
        self.scalars_monitor.reset()
        #self.scalars_monitor.update_plot((0,0,0,0,0,5,0,0,0,0,0))
        
    def stopClicked(self):
        self.holdplot = True

    def mufitClicked(self):
        fitresults = fit.main(bincontent=n.asarray(self.lifetime_monitor.heights))
        self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])

    def activateMuondecayClicked(self):
        """
        What should be done if we are looking for mu-decays?
        """

        if not self.mainwindow.options.mudecaymode:
            if self.activateMuondecay.isChecked():
                self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")
                msg = "WC 00 EF"
                self.mainwindow.outqueue.put(msg)
                self.logger.info("We sent the following message to DAQ %s" %msg)
                self.logger.warn("Chan 3 is set to Veto, threefold coincidence chosen!")
                self.mainwindow.options.mudecaymode = True
                self.mu_ini = True
                self.mu_label = QtGui.QLabel(tr('MainWindow','We are looking for decaying muons!'))
                self.mainwindow.statusbar.addWidget(self.mu_label)
                self.logger.warning('Might possibly overwrite textfile with decays')
                self.mainwindow.mu_file = open(self.mainwindow.options.decayfilename,'w')		
                self.mainwindow.options.dec_mes_start = datetime.datetime.now()

        else:

            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.mainwindow.statusbar.removeWidget(self.mu_label)
            self.mainwindow.options.mudecaymode = False
            mtime = self.mainwindow.options.dec_mes_start - datetime.datetime.now()
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            newmufilename = self.mainwindow.options.decayfilename.replace("HOURS",str(mtime))
            shutil.move(self.mainwindow.options.decayfilename,newmufilename)
            self.mu_ini = True
     
    def activatePulseanalyzerClicked(self):

        if self.activatePulseanalyzer.isChecked():
            self.mainwindow.options.showpulses = True
            self.logger.info("PulseAnalyzer active %s" %self.mainwindow.options.showpulses.__repr__())
        else:
            self.mainwindow.options.showpulses = False
            self.logger.info("PulseAnalyzer active %s" %self.mainwindow.options.showpulses.__repr__())


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
        
        self.outputfile = open(self.mainwindow.options.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.options.filename))
        self.write_file = True
        self.mainwindow.options.raw_mes_start = datetime.datetime.now()
        self.mainwindow.statusbar.addPermanentWidget(self.file_label)

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
            self.mainwindow.statusbar.addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.timer.stop()
                self.mainwindow.statusbar.removeWidget(self.periodic_status_label)
            except AttributeError:
                pass


 



    def timerEvent(self,ev):
        """Custom timerEvent code, called at timer event receive"""
        # get the scalar information from the card
        self.mainwindow.outqueue.put('DS')

        # we have to know, when we sent the command
        now = time.time()
        # we define an intervall here
        if self.mainwindow.ini:
             self.logger.debug("Ini condition unset!")
             self.mainwindow.lastscalarquery = now
             self.mainwindow.ini = False
        else:
             self.mainwindow.thisscalarquery = now - self.mainwindow.lastscalarquery
             self.mainwindow.lastscalarquery = now
             if self.scalars_result:
                 if not self.holdplot:
                     self.scalars_monitor.update_plot(self.scalars_result)

    
        self.logger.debug("The differcene between two sent 'DS' commands is %4.2f seconds" %self.mainwindow.thisscalarquery)

        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))

        # the mu lifetime histogram 
        if self.mainwindow.options.mudecaymode:
        
            if self.mainwindow.decay:    

                self.logger.info("Adding decays %s" %self.mainwindow.decay)

                # at the moment we are only using the first decay

                decay_times =  [decay_time[0] for decay_time in self.mainwindow.decay]

                self.lifetime_monitor.update_plot(decay_times)

                # as different processes are in action,
                # hopefully this is sufficent!
                # (as the low decay rates expected, I think so:))

                muondecay = self.mainwindow.decay[0]
                self.mainwindow.mu_file.write('Decay ')
                muondecay_time = muondecay[1].replace(' ','_')
                self.mainwindow.mu_file.write(muondecay_time.__repr__() + ' ')
                self.mainwindow.mu_file.write(muondecay[0].__repr__())
                self.mainwindow.mu_file.write('\n')
                self.mainwindow.decay = []


        if self.mainwindow.options.showpulses:

            if self.mainwindow.pulses != None:
                self.pulse_monitor.update_plot(self.mainwindow.pulses)


class MuonicOptions:
    """
    A simple struct which holds the different
    options for the program
    """
    #TODO: alter the constructor in such a way that the options from the command line
    # can passed directly through!

    def __init__(self,timewindow,writepulses,nostatus,user):

        # put the file in the data directory
        # we chose a global format for naming the files -> decided on 18/01/2012
        # we use GMT times
        # " Zur einheitlichen Datenbezeichnung schlage ich folgendes Format vor:
        # JJJJ-MM-TT_y_x_vn.dateiformat (JJJJ-Jahr; MM-Monat; TT-Speichertag bzw.
        # Beendigung der Messung; y: G oder L ausw?hlen, G steht f?r **We add R for rate P for pulses and RW for RAW **
        # Geschwindigkeitsmessung/L f?r Lebensdauermessung; x-Messzeit in Stunden;
        # v-erster Buchstabe Vorname; n-erster Buchstabe Familienname)."
        # TODO: consistancy....        
 
        date = time.gmtime()

        # this is hard-coded! There must be a better solution...
        # if you change here, you have to change in setup.py!
        datapath = os.getenv('HOME') + os.sep + 'muonic_data'
 
        self.filename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"R",user[0],user[1]) )
        # the time when the rate measurement is started
        now = datetime.datetime.now()
        self.rate_mes_start = now     
        self.rawfilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"RAW",user[0],user[1]) )
        self.raw_mes_start = False
        self.decayfilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"L",user[0],user[1]) )
        if writepulses:
                self.pulsefilename = os.path.join(datapath,"%i-%i-%i_%i-%i-%i_%s_HOURS_%s%s" %(date.tm_year,date.tm_mon,date.tm_mday,date.tm_hour,date.tm_min,date.tm_sec,"P",user[0],user[1]) )
                self.pulse_mes_start = now
        else:
                self.pulsefilename = ''
                self.pulse_mes_start = False

        # other options...
        self.timewindow = timewindow
        self.nostatus = nostatus
        self.softveto = False
        self.mudecaymode = False
        self.showpulses = False

