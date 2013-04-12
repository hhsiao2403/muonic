"""
Provide the different physics widgets
"""


# Qt4 imports
from PyQt4 import QtGui
from PyQt4 import QtCore

#muonic imports
from LineEdit import LineEdit
from MuonicPlotCanvases import ScalarsCanvas,LifetimeCanvas,PulseCanvas,VelocityCanvas,PulseWidthCanvas
from MuonicDialogs import DecayConfigDialog,PeriodicCallDialog, VelocityConfigDialog
from ..analysis.fit import main as fit
from ..analysis.fit import gaussian_fit
from ..analysis.PulseAnalyzer import VelocityTrigger,DecayTriggerThorough
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

import datetime

import os
import shutil
import numpy as n
import time

tr = QtCore.QCoreApplication.translate

C = 29979245000 # cm/s

class RateWidget(QtGui.QWidget):
    """
    Display rate plot
    """
    def __init__(self,logger,parent = None):
        QtGui.QWidget.__init__(self,parent = parent)
        self.mainwindow = self.parentWidget()
        self.logger           = logger
        self.holdplot         = False
        self.scalars_result   = False 
        self.scalars_monitor  = ScalarsCanvas(self, logger)
        self.rates            = None
        self.rate_mes_start   = datetime.datetime.now()
        self.previous_ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        self.ch_counts = {"ch0" : 0 ,"ch1" : 0,"ch2" : 0,"ch3": 0}
        # buttons for restart/clear the plot rate plot   
        self.start_button = QtGui.QPushButton(tr('MainWindow', 'Restart'))
        self.stop_button  = QtGui.QPushButton(tr('MainWindow', 'Stop'))
        self.lastscalarquery = 0
        self.thisscalarquery = time.time()
        #self.pulses_to_show = None
        self.data_file = open(self.mainwindow.options.filename, 'w')
        self.data_file.write('time | chan0 | chan1 | chan2 | chan3 | R0 | R1 | R2 | R3 | trigger | Delta_time \n')
        
        # always write the rate plot data
        self.data_file_write = True

        QtCore.QObject.connect(self.start_button,
                              QtCore.SIGNAL("clicked()"),
                              self.startClicked
                              )

        QtCore.QObject.connect(self.stop_button,
                              QtCore.SIGNAL("clicked()"),
                              self.stopClicked
                              )

        ntb = NavigationToolbar(self.scalars_monitor, self)
        rate_widget = QtGui.QGridLayout(self)
        rate_widget.addWidget(self.scalars_monitor,0,0,1,3)
        rate_widget.addWidget(ntb,1,0)
        rate_widget.addWidget(self.start_button,1,1)
        rate_widget.addWidget(self.stop_button,1,2)

    def calculate(self,rates):
        #now = time.time()
        #self.thisscalarquery = now - self.lastscalarquery
        #self.lastscalarquery = now
        self.rates = rates

    def update(self):
        if not self.holdplot:
            self.scalars_monitor.update_plot(self.rates)
      
    def is_active(self):
        return True # rate widget is always active    

    def startClicked(self):
        """
        restart the rate measurement
        """ 
        self.logger.debug("Restart Button Clicked")
        self.holdplot = False
        self.scalars_monitor.reset()
        
    def stopClicked(self):
        """
        hold the rate measurement plot till buttion is pushed again
        """
        self.holdplot = True


class PulseanalyzerWidget(QtGui.QWidget): # not used yet
    """
    Provide a widget which is able to show a plot of triggered pulses
    """        
    def __init__(self,logger):
        QtGui.QWidget.__init__(self)
        activatePulseanalyzer = QtGui.QCheckBox(self)
        activatePulseanalyzer.setText(tr("Dialog", "Show oscilloscope as well as the pulswidths", None, QtGui.QApplication.UnicodeUTF8))
        activatePulseanalyzer.setToolTip(QtCore.QString("The oscilloscope will show the last triggered pulses in the selected time window"))
        activatePulseanalyzer.setObjectName("activate_pulseanalyzer")
        grid = QtGui.QGridLayout(self)
        self.pulsecanvas = PulseCanvas(self,logger)
        self.pulsecanvas.setObjectName("pulse_canvas")
        self.pulsewidthcanvas = PulseWidthCanvas(self,logger)
        self.pulsewidthcanvas.setObjectName("pulse_width_canvas")
        ntb = NavigationToolbar(self.pulsecanvas, self)
        ntb2 = NavigationToolbar(self.pulsewidthcanvas, self)
        
        grid.addWidget(activatePulseanalyzer,0,0,1,2)
        grid.addWidget(self.pulsecanvas,1,0)
        grid.addWidget(ntb,2,0) 
        grid.addWidget(self.pulsewidthcanvas,1,1)
        grid.addWidget(ntb2,2,1)
        self.pulses      = None
        self.pulsewidths = []
        # more functional objects        

    def is_active(self):
        return self.findChild(QtGui.QCheckBox,QtCore.QString("activate_pulseanalyzer")).isChecked()


    def calculate(self,pulses):
        self.pulses = pulses
        pulsewidths = [fe - le for chan in pulses[1:] for le,fe in chan]
        self.pulsewidths += pulsewidths
        
    def update(self):
        self.pulsecanvas.update_plot(self.pulses)
        self.pulsewidthcanvas.update_plot(self.pulsewidths)
        self.pulsewidths = []

class VelocityWidget(QtGui.QWidget):

    def __init__(self,logger):
        QtGui.QWidget.__init__(self)
        self.upper_channel = 0
        self.lower_channel = 1
        self.trigger = VelocityTrigger(logger)
        self.times = []
        self.active = False
        self.channel_distance = 100. # in cm
        
        #self.velocitycanvas = VelocityCanvas(logger)

        activateVelocity = QtGui.QCheckBox(self)
        activateVelocity.setText(tr("Dialog", "Measure muon velocity", None, QtGui.QApplication.UnicodeUTF8))
        activateVelocity.setObjectName("activate_velocity")
        self.velocityfit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!')) 
        layout = QtGui.QGridLayout(self)
        layout.addWidget(activateVelocity,0,0,1,2)
        self.velocitycanvas = VelocityCanvas(self,logger)
        self.velocitycanvas.setObjectName("velocity_plot")
        layout.addWidget(self.velocitycanvas,1,0,1,2)
        ntb = NavigationToolbar(self.velocitycanvas, self)
        layout.addWidget(ntb,2,0)
        layout.addWidget(self.velocityfit_button,2,1)      
        QtCore.QObject.connect(activateVelocity,
                               QtCore.SIGNAL("clicked()"),
                               self.activateVelocityClicked
                               )
        QtCore.QObject.connect(self.velocityfit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.velocityFitClicked
                              )
        
    def calculate(self,pulses):
        flighttime = self.trigger.trigger(pulses,upperchannel=self.upper_channel,lowerchannel=self.lower_channel)
        if (flighttime != None and flighttime > 0):
            velocity = (self.channel_distance/((10**(-9))*flighttime))/C #flighttime is in ns, return in fractions of C
            #print flighttime,velocity,self.channel_distance
            if flighttime != None:
                self.times.append(velocity)
                
        
        #print self.times
    #FIXME: we should not name this update
    #since update is already a member
    def update(self):
        self.findChild(VelocityCanvas,QtCore.QString("velocity_plot")).update_plot(self.times)
        self.times = []

    def is_active(self):
        return self.active
    
    def velocityFitClicked(self):
        """
        fit the muon velocity histogram
        """
        fitresults = gaussian_fit(bincontent=n.asarray(self.velocitycanvas.heights))
        self.velocitycanvas.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])


    def activateVelocityClicked(self):
        """
        Perform extra actions when the checkbox is clicked
        """
        if not self.active:
            
            config_dialog = VelocityConfigDialog()
            rv = config_dialog.exec_()
            if rv == 1:
                for chan,ch_label in enumerate(["0","1","2","3"]):
                    if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("uppercheckbox_" + ch_label )).isChecked():
                        self.upper_channel = chan + 1 # ch index is shifted
                        
                for chan,ch_label in enumerate(["0","1","2","3"]):
                    if config_dialog.findChild(QtGui.QRadioButton,QtCore.QString("lowercheckbox_" + ch_label )).isChecked():
                        self.lower_channel = chan + 1 #
            
            self.channel_distance = config_dialog.findChild(QtGui.QSpinBox,QtCore.QString("channel_distance")).value()            
            self.active = True            
        else:
            self.active = False                

class DecayWidget(QtGui.QWidget): 
    
    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent) 
        self.logger = logger 
        self.mufit_button = QtGui.QPushButton(tr('MainWindow', 'Fit!'))
        self.lifetime_monitor = LifetimeCanvas(self,logger)
        self.minsinglepulsewidth = 0
        self.maxsinglepulsewidth = 100000 #inf
        self.mindoublepulsewidth = 0
        self.maxdoublepulsewidth = 100000 #inf
        self.muondecaycounter = 0
        self.lastdecaytime    = 'None'
            
        self.singlepulsechannel = 0
        self.doublepulsechannel = 1
        self.vetopulsechannel   = 2 
        self.decay_mintime      = 0
        self.decay_selfveto     = False
        self.active             = False
        self.trigger = DecayTriggerThorough(logger)
        self.decay              = []
        self.mu_file            = open("/dev/null","w") 
        self.dec_mes_start      = None


        QtCore.QObject.connect(self.mufit_button,
                              QtCore.SIGNAL("clicked()"),
                              self.mufitClicked
                              )


        ntb1 = NavigationToolbar(self.lifetime_monitor, self)

        # activate Muondecay mode with a checkbox
        activateMuondecay = QtGui.QCheckBox(self)
        activateMuondecay.setObjectName("activate_mudecay")
        activateMuondecay.setText(tr("Dialog", "Check for decayed Muons \n- Warning! this will define your coincidence/Veto settings!", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(activateMuondecay,
                              QtCore.SIGNAL("clicked()"),
                              self.activateMuondecayClicked
                              )
        displayMuons                 = QtGui.QLabel(self)
        displayMuons.setObjectName("muoncounter")
        lastDecay                    = QtGui.QLabel(self)
        lastDecay.setObjectName("lastdecay")
 
        decay_tab = QtGui.QGridLayout(self)
        decay_tab.addWidget(activateMuondecay,0,0)
        decay_tab.addWidget(displayMuons,1,0)
        decay_tab.addWidget(lastDecay,2,0)
        decay_tab.addWidget(self.lifetime_monitor,3,0,1,2)
        decay_tab.addWidget(ntb1,4,0)
        decay_tab.addWidget(self.mufit_button,4,1)
        self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
        self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
        
        #self.decaywidget = self.widget(1)

    def is_active(self):
        return self.active
     
    def calculate(self,pulses):
        #single_channel = self.options.singlepulsechannel, double_channel = self.options.doublepulsechannel, veto_channel = self.options.vetopulsechannel,selfveto = self.options.decay_selfveto,mindecaytime = self.options.decay_mintime,minsinglepulsewidth = minsinglepulsewidth,maxsinglepulsewidth = maxsinglepulsewidth, mindoublepulsewidth = mindoublepulsewidth, maxdoublepulsewidth = maxdoublepulsewidth):
        decay =  self.trigger.trigger(pulses,single_channel = self.singlepulsechannel,double_channel = self.doublepulsechannel, veto_channel = self.vetopulsechannel, selfveto = self.decay_selfveto, mindecaytime= self.decay_mintime,minsinglepulsewidth = self.minsinglepulsewidth,maxsinglepulsewidth = self.maxsinglepulsewidth, mindoublepulsewidth = self.mindoublepulsewidth, maxdoublepulsewidth = self.maxdoublepulsewidth )
        if decay != None:
            when = time.asctime()
            self.decay.append((decay/1000,when))
            #devide by 1000 to get microseconds
            
            self.logger.info('We have found a decaying muon with a decaytime of %f at %s' %(decay,when)) 
            self.muondecaycounter += 1
            self.lastdecaytime = when
      
    def mufitClicked(self):
        """
        fit the muon decay histogram
        """
        fitresults = fit(bincontent=n.asarray(self.lifetime_monitor.heights))
        self.lifetime_monitor.show_fit(fitresults[0],fitresults[1],fitresults[2],fitresults[3],fitresults[4],fitresults[5],fitresults[6],fitresults[7])

    def update(self):
        if self.decay:
            decay_times =  [decay_time[0] for decay_time in self.decay]
            self.lifetime_monitor.update_plot(decay_times)
            self.findChild(QtGui.QLabel,QtCore.QString("muoncounter")).setText(tr("Dialog", "We have %i decayed muons " %self.muondecaycounter, None, QtGui.QApplication.UnicodeUTF8))
            self.findChild(QtGui.QLabel,QtCore.QString("lastdecay")).setText(tr("Dialog", "Last detected decay at time %s " %self.lastdecaytime, None, QtGui.QApplication.UnicodeUTF8))
            for muondecay in self.decay:
                #muondecay = self.decay[0] 
                muondecay_time = muondecay[1].replace(' ','_')
                self.mu_file.write('Decay ')
                self.mu_file.write(muondecay_time.__repr__() + ' ')
                self.mu_file.write(muondecay[0].__repr__())
                self.mu_file.write('\n')
                self.decay = []
        else:
            pass


    def activateMuondecayClicked(self):
        """
        What should be done if we are looking for mu-decays?
        """
 
        now = datetime.datetime.now()
        #if not self.mainwindow.options.mudecaymode:
        if not self.active:
                #self.decaywidget.findChild(QtGui.QCheckBox,QtCore.QString("activate_mudecay")).setChecked(True)

                # launch the settings window
                config_window = DecayConfigDialog()
                rv = config_window.exec_()
                if rv == 1:

                    chan0_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_0")).isChecked()
                    chan1_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_1")).isChecked()
                    chan2_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_2")).isChecked()
                    chan3_single = config_window.findChild(QtGui.QRadioButton,QtCore.QString("singlecheckbox_3")).isChecked()
                    chan0_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_0")).isChecked()
                    chan1_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_1")).isChecked()
                    chan2_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_2")).isChecked()
                    chan3_double = config_window.findChild(QtGui.QRadioButton,QtCore.QString("doublecheckbox_3")).isChecked()
                    chan0_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_0")).isChecked()
                    chan1_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_1")).isChecked()
                    chan2_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_2")).isChecked()
                    chan3_veto   = config_window.findChild(QtGui.QRadioButton,QtCore.QString("vetocheckbox_3")).isChecked()
                    self.decay_selfveto  = config_window.selfveto.isChecked()
                    self.decay_mintime   = int(config_window.mintime.value())
                    if config_window.findChild(QtGui.QGroupBox,QtCore.QString("pulsewidthgroupbox")).isChecked():
                        self.minsinglepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("minsinglepulsewidth")).value())
                        self.maxsinglepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("maxsinglepulsewidth")).value())
                        self.mindoublepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("mindoublepulsewidth")).value())
                        self.maxdoublepulsewidth = int(config_window.findChild(QtGui.QSpinBox,QtCore.QString("maxdoublepulsewidth")).value())
                    
                    for channel in enumerate([chan0_single,chan1_single,chan2_single,chan3_single]):
                        if channel[1]:
                            self.singlepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset
                # FIXME! 
                    for channel in enumerate([chan0_double,chan1_double,chan2_double,chan3_double]):
                        if channel[1]:
                            self.doublepulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset

                    for channel in enumerate([chan0_veto,chan1_veto,chan2_veto,chan3_veto]):
                        if channel[1]:
                            self.vetopulsechannel = channel[0] + 1 # there is a mapping later from this to an index with an offset

                self.logger.warn("We now activate the Muondecay mode!\n All other Coincidence/Veto settings will be overriden!")

                self.logger.warning("Changing gate width and enabeling pulses") 
                self.logger.info("Looking for single pulse in Channel %i" %(self.singlepulsechannel - 1))
                self.logger.info("Looking for double pulse in Channel %i" %(self.doublepulsechannel - 1 ))
                self.logger.info("Using veto pulses in Channel %i"        %(self.vetopulsechannel - 1 ))

                self.mu_label = QtGui.QLabel(tr('MainWindow','Muon Decay measurement active!'))
                self.parentWidget().parentWidget().parentWidget().statusbar.addPermanentWidget(self.mu_label)
                self.parentWidget().parentWidget().parentWidget().outqueue.put("CE") 
                self.parentWidget().parentWidget().parentWidget().outqueue.put("WC 03 04")
              
                self.mu_file = open(self.parentWidget().parentWidget().parentWidget().options.decayfilename,'w')        
                self.dec_mes_start = now
                #self.decaywidget.findChild("activate_mudecay").setChecked(True)
                self.active = True

        else:
            #self.decaywidget.findChild(QtGui.QCheckBox,QtCore.QString("activate_mudecay")).setChecked(False)

            self.logger.info('Muondecay mode now deactivated, returning to previous setting (if available)')
            self.parentWidget().parentWidget().parentWidget().statusbar.removeWidget(self.mu_label)
            #self.parentWidget().parentWidget().parentWidget().options.mudecaymode = False
            mtime = now - self.dec_mes_start
            mtime = round(mtime.seconds/(3600.),2) + mtime.days *86400
            self.logger.info("The muon decay measurement was active for %f hours" % mtime)
            newmufilename = self.parentWidget().parentWidget().parentWidget().options.decayfilename.replace("HOURS",str(mtime))
            shutil.move(self.parentWidget().parentWidget().parentWidget().options.decayfilename,newmufilename)
            self.active = False

class DAQWidget(QtGui.QWidget):

    def __init__(self,logger,parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.mainwindow = self.parentWidget()
        
        self.write_file       = False
        self.label           = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit      = LineEdit()
        self.hello_button    = QtGui.QPushButton(tr('MainWindow','Send'))
        self.file_button     = QtGui.QPushButton(tr('MainWindow', 'Save to File'))
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
        
        daq_layout = QtGui.QGridLayout(self)
        daq_layout.addWidget(self.text_box,0,0,1, 4)
        daq_layout.addWidget(self.label,1,0)
        daq_layout.addWidget(self.hello_edit,1,1)
        daq_layout.addWidget(self.hello_button,1,2) 
        daq_layout.addWidget(self.file_button,1,2) 
        daq_layout.addWidget(self.periodic_button,1,3)   

    def on_hello_clicked(self):

        """
        send a message to the daq
        """
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.mainwindow.outqueue.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        """
        save the raw daq data to a automatically named file
        """       
        self.outputfile = open(self.mainwindow.options.rawfilename,"w")
        self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%self.mainwindow.options.rawfilename))
        self.write_file = True
        self.mainwindow.options.raw_mes_start = datetime.datetime.now()
        self.mainwindow.statusbar.addPermanentWidget(self.file_label)

    def on_periodic_clicked(self):
        """
        issue a command periodically
        """

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
            self.periodic_call_timer = QtCore.QTimer()
            QtCore.QObject.connect(self.periodic_call_timer,
                               QtCore.SIGNAL("timeout()"),
                               self.periodic_put)
            self.periodic_put()
            self.periodic_call_timer.start(period)
            self.periodic_status_label = QtGui.QLabel(tr('MainWindow','%s every %s sec'%(command,period/1000)))
            self.mainwindow.statusbar.addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.periodic_call_timer.stop()
                self.mainwindow.statusbar.removeWidget(self.periodic_status_label)
            except AttributeError:
                pass
