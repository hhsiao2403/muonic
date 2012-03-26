"""
Provides the main window for the gui part of muonic
"""

# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

# multithreading imports
import Queue

# muonic imports
#from LineEdit import LineEdit
#from PeriodicCallDialog import PeriodicCallDialog
from ThresholdDialog import ThresholdDialog
from ConfigDialog import ConfigDialog
from OptionsDialog import OptionsDialog
from HelpDialog import HelpDialog
from TabWidget import TabWidget

#from muonic.gui.live.scalarsmonitor import ScalarsMonitor
#from muonic.gui.live.lifetimemonitor import LifetimeMonitor
#from muonic.gui.live.pulsemonitor import PulseMonitor
#
#from muonic.analysis import fit

import muonic.analysis.PulseAnalyzer as pa
#import get_time

#from matplotlib.backends.backend_qt4agg \
#import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time



tr = QtCore.QCoreApplication.translate

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, logger, opts, root, win_parent = None):

        # instanciate the mainwindow

        self.reso_w = 600
        self.reso_h = 400


        self.logger = logger
        self.options = MuonicOptions(float(opts.timewindow),opts.writepulses,opts.nostatus,opts.user)
        self.ini = True  # is it the first time all the functions are called?
        self.mu_ini = True # is it the first time thet the mudecaymode is started?        

        # this holds the scalars in the time interval
        self.channel_counts = [0,0,0,0,0] #[trigger,ch0,ch1,ch2,ch3]

        # keep the last decays
        self.decay = []

        # last time, when the 'DS' command was sent
        self.lastscalarquery = 0
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
        self.resize(self.reso_w, self.reso_h)

        windowtitle = QtCore.QString("muonic") 
        self.setWindowTitle(windowtitle)
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
       
        self.tabwidget = TabWidget(self, self.options.timewindow, self.logger)       
        self.setCentralWidget(self.tabwidget)

        # provide buttons to exit the application
        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))

        self.connect(exit, QtCore.SIGNAL('triggered()'), self.exit_program)
        self.connect(self, QtCore.SIGNAL('closeEmitApp()'), QtCore.SLOT('close()') )

        # prepare the config menu
        config = QtGui.QAction(QtGui.QIcon(''),'Channel Configuration', self)
        config.setStatusTip(tr('MainWindow','Configure the Coincidences and channels'))
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
 
    def exit_program(self,*args):
        """
        This function is used either with the 'x' button
        (then an event has to be passed)
        Or it is used with the File->Exit button, than no event
        will be passed.
        """

        ev = False
        if args:
            ev = args[0]
        # ask kindly if the user is really sure if she/he wants to exit
        reply = QtGui.QMessageBox.question(self, 'Attention!',
                'Do you really want to exit?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            now = datetime.datetime.now()

            # close the RAW file (if any)
            if self.tabwidget.write_file:
                self.tabwidget.write_file = False
                mtime = now - self.options.raw_mes_start
                mtime = round(mtime.seconds/(3600.),2) + mtime.days*86400
                self.logger.info("The raw data was written for %f hours" % mtime)
                newrawfilename = self.options.rawfilename.replace("HOURS",str(mtime))
                shutil.move(self.options.rawfilename,newrawfilename)
                self.tabwidget.outputfile.close()

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
            self.tabwidget.writefile = False
            try:
                self.mu_file.close()
 
            except AttributeError:
                pass

            self.root.quit()           
            self.emit(QtCore.SIGNAL('closeEmitApp()'))

        else:
            if ev:
                ev.ignore()
            else:
                pass
    
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
                self.tabwidget.scalars_monitor.do_not_show_trigger = True
            else:
                self.tabwidget.scalars_monitor.do_not_show_trigger = False
            
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
        help_window = HelpDialog()
        help_window.exec_()

    def clear_function(self):
        self.logger.debug("Clear was called")
        self.tabwidget.scalars_monitor.reset()

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
                self.tabwidget.text_box.appendPlainText(str(msg))
                if self.tabwidget.write_file:
                    try:
                        if self.options.nostatus:
                            fields = msg.rstrip("\n").split(" ")
                            if ((len(fields) == 16) and (len(fields[0]) == 8)):
                                self.tabwidget.outputfile.write(str(msg)+'\n')
                            else:
                                self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
                        else:
                            self.tabwidget.outputfile.write(str(msg)+'\n')

                    except ValueError:
			self.logger.info('Trying to write on closed file, captured!')


		# check for threshold information
                if msg.startswith('TL') and len(msg) > 3:
                    msg = msg.split('=')
                    self.threshold_ch0 = msg[1][:-2]
                    self.threshold_ch1 = msg[2][:-2]
                    self.threshold_ch2 = msg[3][:-2]
                    self.threshold_ch3 = msg[4]
                    return  

                if msg.startswith('ST'):
                    return

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
                        self.tabwidget.scalars_result = (self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window, self.scalars_diff_trigger/time_window, time_window, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_trigger)
                        #write the rates to data file
                        # we have to catch IOErrors, can occur if program is 
                        # exited
                        if self.data_file_write:
                            try:
                                self.data_file.write('%f %f %f %f %f %f %f %f %f %f %f \n' % (self.scalars_time, self.scalars_diff_ch0, self.scalars_diff_ch1, self.scalars_diff_ch2, self.scalars_diff_ch3, self.scalars_diff_ch0/time_window,self.scalars_diff_ch1/time_window,self.scalars_diff_ch2/time_window,self.scalars_diff_ch3/time_window,self.scalars_diff_trigger/time_window,time_window))
                                self.logger.debug("Rate plot data was written to %s" %self.data_file.__repr__())
                            except ValueError:
                                self.logger.warning("ValueError, Rate plot data was not written to %s" %self.data_file.__repr__())

                # check for other status messages          
                elif len(msg) < 50:
                    #it is most propably a status message (poor criterion)
                    return
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
                                if self.options.decaytrigger == "simple":
                                    self.dtrigger = pa.DecayTriggerSimple(self.pulses,self.options.softveto)
                                if self.options.decaytrigger == "single":
                                    self.dtrigger = pa.DecayTriggerSingle(self.pulses,self.options.softveto)
                                if self.options.decaytrigger == "thorough":
                                    self.dtrigger = pa.DecayTriggerThorough(self.pulses,self.options.softveto)
              
                                self.mu_ini = False 
                                            
                            else:
                                tmpdecay = self.dtrigger.trigger(self.pulses)                   
                                if tmpdecay != None:
                                    when = time.asctime()
                                    self.decay.append((tmpdecay/100.,when))
                                    self.logger.info('We have found a decaying muon with a decaytime of %f at %s' %(tmpdecay,when)) 
                                    self.tabwidget.muondecaycounter += 1
                                    self.tabwidget.lastdecaytime = when

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
        self.decaytrigger = False
