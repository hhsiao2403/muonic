# for command-line arguments
import pylab as p
import numpy as n
# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui
# Matplotlib Figure object
from matplotlib.figure import Figure
import matplotlib.patches as patches

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas
# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

class ScalarsMonitor(FigureCanvas):
    """Matplotlib Figure widget to display a plot of the rates"""
    def __init__(self, parent, timewindow, logger):
       
        self.logger = logger
        self.timewindow = timewindow
        #print "debug in sclasers monitor", self.debug

        
        #max length of shown plot is 10 minutes!
        self.MAXLENGTH = 40
        
        self.highest=0
        self.lowest=0

        # first image setup
        self.fig = Figure(facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(right=0.7)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-5, 100)
        self.ax.grid()
        #self.ax.set_title('Rate')
        self.ax.set_xlabel('time in s')
        self.ax.set_ylabel('Rate in Hz')
        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)
        #self.ax.set_autoscale_on(True)
        # generates first "empty" plots
        self.time_window = 0
        self.chan0, self.chan1, self.chan2, self.chan3, self.trigger, self.l_time =[], [], [], [], [], []
        self.l_chan0, = self.ax.plot([],self.chan0, c='y', label='chan0',lw=3)
        self.l_chan1, = self.ax.plot([],self.chan1, c='m', label='chan1',lw=3)
        self.l_chan2, = self.ax.plot([],self.chan2, c='c',  label='chan2',lw=3)
        self.l_chan3, = self.ax.plot([],self.chan3, c='b', label='chan3',lw=3)
        self.l_trigger, = self.ax.plot([],self.chan3, c='g', label='trigger',lw=3)
	# add legend to plot
        #self.ax.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        #catch error which occurs sometimes for some 
        #pylab versions
        #try:
         #   self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        #except(TypeError):
        #except:
        self.ax.legend()

        # force a redraw of the Figure
        self.fig.canvas.draw()
        # initialize the iteration counter
        self.cnt = 0

        self.logger.debug("chan 0 %s" %self.l_chan0)
        self.setParent(parent)
       

    def update_plot(self, result):

        
        #do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()
        #self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        #FigureCanvas.__init__(self, self.fig)
        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-5, 100)
        self.ax.grid()
        #self.ax.set_title('Rate')
        self.ax.set_xlabel('time in s')
        self.ax.set_ylabel('Rate in Hz')
        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)
        #self.ax.set_autoscale_on(True)
        try:
            self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        except(TypeError):
            self.ax.legend()



        self.logger.debug("Result %s" %result.__repr__())
        # update lines data using the lists with new data
        self.chan0.append(result[0])
        self.chan1.append(result[1])
        self.chan2.append(result[2])
        self.chan3.append(result[3])
        self.trigger.append(result[4])
        self.time_window += result[5]
        self.l_time.append(self.time_window)

        if len(self.chan0) >  self.MAXLENGTH:
            self.chan0.remove(self.chan0[0])
            self.chan1.remove(self.chan1[0])
            self.chan2.remove(self.chan2[0])
            self.chan3.remove(self.chan3[0])
            self.trigger.remove(self.trigger[0])
            self.l_time.remove(self.l_time[0])

      
        self.logger.debug("self.l_chan0 %s %s" %(self.l_chan0, type(self.l_chan0)))
        self.l_chan0, = self.ax.plot(self.l_time,self.chan0, c='y', label='chan0',lw=2)
        self.l_chan1, = self.ax.plot(self.l_time,self.chan1, c='m', label='chan1',lw=2)
        self.l_chan2, = self.ax.plot(self.l_time,self.chan2, c='c', label='chan2',lw=2)
        self.l_chan3, = self.ax.plot(self.l_time,self.chan3, c='b', label='chan3',lw=2)
        self.l_trigger, = self.ax.plot(self.l_time,self.trigger, c='g', label='trigger',lw=2)



        #self.l_chan0.set_data(self.l_time, self.chan0)
        #self.l_chan1.set_data(self.l_time, self.chan1)
        #self.l_chan2.set_data(self.l_time, self.chan2)
        #self.l_chan3.set_data(self.l_time, self.chan3)
        #self.l_trigger.set_data(self.l_time, self.trigger)
        #       

        ma2 = max( max(self.chan0), max(self.chan1), max(self.chan2), 
                   max(self.chan3))
        mi2 = min( min(self.chan0), min(self.chan1), min(self.chan2), 
                   min(self.chan3), min(self.trigger))
        
        if ma2 > self.highest:
            self.highest = ma2
        if mi2 < self.lowest:
            self.lowest = mi2
        
        self.logger.debug("Chan0 to plot %s" %self.chan0.__repr__())
        ma = max( max(self.chan0), max(self.chan1), max(self.chan2), 
                  max(self.chan3), max(self.trigger)  )
        self.ax.set_ylim(0, ma*1.1)
        self.ax.set_xlim(self.l_time[0], self.l_time[-1])
        #if self.debug: print 'SCALARSMONITOR self.chan0', self.chan0 
        string = 'channel0 = %.1f Hz \nchannel1 = %.1f Hz \nchannel2 = %.1f Hz \nchannel3 = %.1f Hz \ntrigger = %.1f Hz \n\nrunning for %.2f h \nmax rate = %.1f Hz \nmin rate = %.1f Hz \ntime window = %.1f s' % ( n.array(self.chan0).mean(), n.array(self.chan1).mean(), n.array(self.chan2).mean(), n.array(self.chan3).mean(), n.array(self.trigger).mean(), self.l_time[-1]/3600.0, ma2, mi2, self.timewindow)
        
        #patch = patches.Rectangle(
        #    (1.1, 0.0), 0.8, 1,
        #    fill=True, edgecolor=None, facecolor='blue', transform=self.ax.transAxes, clip_on=False)
        #self.ax.add_patch(patch)

        self.ax.text(1.05, 0.0, string, transform=self.ax.transAxes)#, bbox=dict(facecolor = 'white', alpha=1, pad=20))
        
        

#         self.ax.text(1.05, 1.0, 'ch0  %1.f Hz \n' %n.array(self.chan0).mean(), transform=self.ax.transAxes, bbox=dict(facecolor = 'white', alpha=1)
#         self.ax.text(1, 0.9, 'ch1  %1.f Hz' %n.array(self.chan1).mean(), transform=self.ax.transAxes, bbox=dict(facecolor = 'white', alpha=1))
#         self.ax.text(1, 0.8, 'ch2  %1.f Hz' %n.array(self.chan2).mean(), transform=self.ax.transAxes, bbox=dict(facecolor = 'white', alpha=1))
#         self.ax.text(1, 0.7, 'ch3  %1.f Hz' %n.array(self.chan3).mean(), transform=self.ax.transAxes, bbox=dict(facecolor = 'white', alpha=1))
#         self.ax.text(1, 0.6, 'trig %1.f Hz' %n.array(self.trigger).mean(), transform=self.ax.transAxes, bbox=dict(facecolor = 'white', alpha=1))
#         
        self.ax.legend()
        self.fig.canvas.draw()
        

