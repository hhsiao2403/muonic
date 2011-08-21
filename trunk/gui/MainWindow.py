from PyQt4 import QtGui
from PyQt4 import QtCore

# for exceptions
import Queue

# parts of the program
from gui.LineEdit import LineEdit
from gui.PeriodicCallDialog import PeriodicCallDialog
from gui.ThresholdDialog import ThresholdDialog
from gui.ConfigDialog import ConfigDialog
from gui.OptionsDialog import OptionsDialog
from gui.HelpWindow import HelpWindow
from gui.live.scalarsmonitor import ScalarsMonitor
from gui.live.lifetimemonitor import LifetimeMonitor
from gui.live.pulsemonitor import PulseMonitor
import PulseAnalyzer as pa


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

#define some global variables 
CURRENTDAQSTATUS = dict()
LASTQUERY = time.time()


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, filename, logger, timewindow, win_parent = None):

        # instanciate the mainwindow
        self.logger = logger
        self.options = MuonicOptions(filename,timewindow)
        self.options.filename = filename             
        self.options.timewindow = timewindow
        self.ini = True  # is it the first time all the functions are called?
        self.mu_ini = True # is it the first time thet the mudecaymode is started?        

        # some hardware info
        #assuming the cpld clock runs with approx 41MHz
        self.cpld_tick = 24  #nsec 


        # keep the last decays
        self.decay = []

        # last time, when the 'DS' command was sent
        self.lastscalarquery = time.time()
        self.thisscalarquery = time.time()
              
        # the pulseextractor for direct analysis
        self.pulseextractor = pa.PulseExtractor() 
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

        self.inqueue = inqueue
        self.outqueue = outqueue
        # we have to ensure that the DAQcard does not sent
        # any automatic status reports every x seconds
        self.outqueue.put('ST N!=1')
        self.outqueue.put('ST 0')

        self.endcommand = endcommand

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

        # prepare the threshold menu
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip(tr('MainWindow','Set trigger thresholds'))
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
        
        # prepare the config menu
        config = QtGui.QAction(QtGui.QIcon(''),'Channel Configuration', self)
        config.setStatusTip(tr('MainWindow','Configuer the Coincidences and channels'))
        self.connect(config, QtCore.SIGNAL('triggered()'), self.config_menu)
        
        # the options menu
        options = QtGui.QAction(QtGui.QIcon(''),'Options', self)
        options.setStatusTip(tr('MainWindow','Set program options'))
        self.connect(options, QtCore.SIGNAL('triggered()'), self.options_menu)


        # the clear button
        clear = QtGui.QAction(QtGui.QIcon(''),'Clear rate plot', self)
        clear.setStatusTip(tr('MainWindow','clear plots'))
       
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)
        scalars = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'Scalars', self)
        self.connect(clear, QtCore.SIGNAL('triggered()'), self.clear_function)

        # create the menubar and fill it with the submenus
       
        menubar = self.menuBar()
        file = menubar.addMenu(tr('MainWindow','&File'))
        file.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(thresholds)
        settings.addAction(config)
        settings.addAction(clear)
        settings.addAction(options)

        help = menubar.addMenu(tr('MainWindow','&Help'))
        help.addAction(helpdaqcommands)

        ## keep as example but takes to much space at the moment
        # add a toolbar and add some icons to it
        # toolbar = self.addToolBar(tr('MainWindow','Exit'))
        # toolbar.addAction(exit)

    # exit the main program after verification
    def verification(self, question_string):
        reply = QtGui.QMessageBox.question(self, 'Message',
                question_string, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False
    
    def exit_program(self):
        if self.verification('Do you really want to exit?'):
            self.logger.debug('Exit!')
            self.endcommand()
            self.emit(QtCore.SIGNAL('closeEmitApp()'))
        else:
	    pass        
    
    #the individual menus
    def threshold_menu(self):
        threshold_window = ThresholdDialog()
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
            self.options.usecpld = options_window.CpldCheckbox.isChecked()
            self.logger.info('Using CPLD clock for rates calculation: %s' %self.options.usecpld.__repr__())
            self.options.softveto = options_window.VetoCheckbox.isChecked()
            self.logger.info('Using Chan3 software veto %s' %self.options.softveto.__repr__())
            


    def help_menu(self):
        help_window = HelpWindow()
        help_window.exec_()

    def clear_function(self):
        self.logger.debug("Clear was called")
        self.subwindow.scalars_monitor.reset()

    #this functions gets everything out of the inqueue
    #All calculations should happen here



    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        NEW: It also queries the DAQ with the 'DS' command
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
                        self.subwindow.outputfile.write(str(msg)+'\n')
                    except ValueError:
			self.logger.info('Trying to write on closed file, captured!')

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
                         # if the time window is too small
                         # this can cause an unphysical 
                         # high rate
                        if time_window < 0.5:
                            self.logger.info("time window to small, setting time_window = 0.5")
                            time_window = 0.5
                         
                         #send the counted scalars to the subwindow
                        self.subwindow.scalars_result = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_trigger)
                        #if self.scalars_result:
                        #    self.subwindow.scalars_monitor.update_plot(self.scalars_result)
                        #write the rates to data file
                        # we have to catch IOErrors, can occur if program is 
                        # exited
                        try:
                            self.data_file.write('%f %f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_time, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                            self.logger.debug("DATA was written to %s" %self.data_file.__repr__())
                        except ValueError:
                           self.logger.warning("ValueError, DATA was not written to %s" %self.data_file.__repr__())
                           pass                         
                
                elif (self.options.mudecaymode or self.options.showpulses):
                    # we now assume that we are using chan0-2 for data taking anch chan3 as veto
                    self.pulses = self.pulseextractor.extract(msg)
                    # print pulses # we do not really want to do that!

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
                                    self.decay.append(tmpdecay/100.)
                                    when = time.asctime()
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
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        if self.subwindow.write_file:
            self.subwindow.outputfile.close()
        self.data_file.close()
        self.exit_program()


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
       
        self.scalars_monitor = ScalarsMonitor(self, timewindow, self.logger)
        self.lifetime_monitor = LifetimeMonitor(self,self.logger)
        self.pulse_monitor = PulseMonitor(self,self.logger)

        # instantiate the navigation toolbar
        ntb = NavigationToolbar(self.scalars_monitor, self)
        # pack theses widget into the vertical box
        p2_vertical.addWidget(self.scalars_monitor)
        p2_vertical.addWidget(ntb)

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
        p3_vertical.addWidget(ntb2)



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
                self.mu_label = QtGui.QLabel(tr('MainWindow','We are looking for ddecaying muons!'))
                self.mainwindow.statusbar.addWidget(self.mu_label)


        else:

            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.mainwindow.statusbar.removeWidget(self.mu_label)
            self.mainwindow.options.mudecaymode = False
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
        # we define an intervall here
        if not self.mainwindow.options.usecpld:
            if self.mainwindow.ini:
                 self.logger.debug("Ini condition unset!")
                 self.mainwindow.lastscalarquery = time.time()
                 self.mainwindow.ini = False
            else:
                 self.mainwindow.thisscalarquery = time.time() - self.mainwindow.lastscalarquery
                 self.mainwindow.lastscalarquery = time.time()
                 if self.scalars_result:
                     self.scalars_monitor.update_plot(self.scalars_result)

        else:
            if self.mainwindow.ini:
                 while True:
                     timestamp = self.mainwindow.inqueue.get(0)
                     try:
                         timestamp = int(timestamp[0],16)*self.mainwindow.cpld_tick
                         break
                     except ValueError:
                         self.logger.debug("Cant convert to integer")
                         continue
                                              
                 self.logger.debug("Ini condition unset!")
                 self.mainwindow.lastscalarquery = timestamp
                 self.mainwindow.ini = False

            else:
                 while True:
                     timestamp = self.mainwindow.inqueue.get(0)
                     try:
                         timestamp = int(timestamp[0],16)*self.mainwindow.cpld_tick
                         break
                     except ValueError:
                         self.logger.debug("Cant convert to integer")
                         continue
                 
                 self.mainwindow.thisscalarquery = timestamp - self.mainwindow.lastscalarquery
                 self.mainwindow.lastscalarquery = timestamp

                 if self.scalars_result:
                     self.scalars_monitor.update_plot(self.scalars_result)
    
 
        self.logger.debug("The differcene between two sent 'DS' commands is %4.2f seconds" %self.mainwindow.thisscalarquery)


        #for debugging: check the garbage collector
        self.logger.debug("%s objects traced by GC" %len(gc.get_objects()))
        self.logger.debug("All objects collected! by GC")
        self.logger.debug("%s objects were not reachalbe" %gc.collect().__repr__())
        self.logger.debug("%s objects traced by GC " %len(gc.get_objects()))

        self.displayMuons.setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.lastDecay.setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))

        # the mu lifetime histogram 
        if self.mainwindow.options.mudecaymode:


            #mu, sigma = 10, 5

            # toy model, with gauss distribution
            # (that we now this is a simulation :))
            # import random
            # x = random.gauss(mu,sigma)
        
            if self.mainwindow.decay:    
                self.logger.info("Adding decays %s" %self.mainwindow.decay)
                self.lifetime_monitor.update_plot(self.mainwindow.decay)
                # as different processes are in action,
                # hopefully this is sufficent!
                # (as the low decay rates expected, I think so:))
                self.mainwindow.decay = []



        if self.mainwindow.options.showpulses:

            if self.mainwindow.pulses != None:


                self.pulse_monitor.update_plot(self.mainwindow.pulses)

class MuonicOptions:
    """
    A simple struct which holds the different
    options for the program
    """


    def __init__(self,filename,timewindow):
        self.filename = filename
        self.timewindow = timewindow
        self.softveto = False
        self.usecpld = False
        self.mudecaymode = False
        self.showpulses = False



