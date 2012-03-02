# for command-line arguments
import pylab as p
import numpy as n
from datetime import datetime
# Matplotlib Figure object
from matplotlib.figure import Figure
#import matplotlib.patches as patches

# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas
# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar

class ScalarsCanvas(FigureCanvas):
    """Matplotlib Figure widget to Muon rates"""
    def __init__(self, parent, logger):   
                
        self.logger = logger

        self.do_not_show_trigger = False
        
        #max length of shown plot is 10 minutes!
        self.MAXLENGTH = 40
        
        self.fig = Figure(facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.1, right=0.6)

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)

        # set specific limits for X and Y axes
        self.ax.grid()
        self.ax.set_xlabel('time in s')
        self.ax.set_ylabel('rate in Hz')

        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)

        self.reset()


        self.setParent(parent)

        
        
    def reset(self):
        """reseting all data"""

        self.ax.clear()
        self.ax.grid()
        self.ax.set_xlabel('time in s')
        self.ax.set_ylabel('Rate in Hz')

        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)
	

        self.highest=0
        self.lowest=0
        self.now = datetime.now()#.strftime('%d.%m.%Y %H:%M:%S')
        self.ax.set_xlim(0., 5.2)
        self.ax.set_ylim(0., 100.2)
        
        self.time_window = 0
        self.chan0, self.chan1, self.chan2, self.chan3, self.trigger, self.l_time =[0], [0], [0], [0], [0], [0]
        self.l_chan0, = self.ax.plot(self.l_time,self.chan0, c='y', label='ch0',lw=3)
        self.l_chan1, = self.ax.plot(self.l_time,self.chan1, c='m', label='ch1',lw=3)
        self.l_chan2, = self.ax.plot(self.l_time,self.chan2, c='c',  label='ch2',lw=3)
        self.l_chan3, = self.ax.plot(self.l_time,self.chan3, c='b', label='ch3',lw=3)
        if not self.do_not_show_trigger:
            self.l_trigger, = self.ax.plot(self.l_time,self.trigger, c='g', label='trg',lw=3)

        self.N0 = 0
        self.N1 = 0
        self.N2 = 0
        self.N3 = 0
        self.NT = 0
        
        self.fig.canvas.draw()

    def update_plot(self, result):

        
        #do a complete redraw of the plot to avoid memory leak!
        self.ax.clear()

        # set specific limits for X and Y axes
        #self.ax.set_xlim(0, 1)
        #self.ax.set_ylim(-5, 100)
        self.ax.grid()
        self.ax.set_xlabel('time in s')
        self.ax.set_ylabel('Rate in Hz')

        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)


        self.logger.debug("result : %s" %result.__repr__())

        # update lines data using the lists with new data
        self.chan0.append(result[0])
        self.chan1.append(result[1])
        self.chan2.append(result[2])
        self.chan3.append(result[3])
        self.trigger.append(result[4])
        self.time_window += result[5]
        self.l_time.append(self.time_window)
        self.N0 += result[6]
        self.N1 += result[7]
        self.N2 += result[8]
        self.N3 += result[9]
        self.NT += result[10]


        self.l_chan0, = self.ax.plot(self.l_time,self.chan0, c='y', label='ch0',lw=2)
        self.l_chan1, = self.ax.plot(self.l_time,self.chan1, c='m', label='ch1',lw=2)
        self.l_chan2, = self.ax.plot(self.l_time,self.chan2, c='c', label='ch2',lw=2)
        self.l_chan3, = self.ax.plot(self.l_time,self.chan3, c='b', label='ch3',lw=2)
        if not self.do_not_show_trigger:
            self.l_trigger, = self.ax.plot(self.l_time,self.trigger, c='g', label='trg',lw=2)

        try:
            if self.do_not_show_trigger:
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=4, mode="expand", borderaxespad=0., handlelength=2)
            else:
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0., handlelength=2)
            
        except:
            self.logger.info('An error with the legend occured!')
            self.ax.legend(loc=2)
        
        


        if len(self.chan0) >  self.MAXLENGTH:
            self.chan0.remove(self.chan0[0])
            self.chan1.remove(self.chan1[0])
            self.chan2.remove(self.chan2[0])
            self.chan3.remove(self.chan3[0])
            self.trigger.remove(self.trigger[0])
            self.l_time.remove(self.l_time[0])

      
        self.logger.debug("self.l_chan0: %s" %self.l_chan0.__repr__())



        ma2 = max( max(self.chan0), max(self.chan1), max(self.chan2), 
                   max(self.chan3))
        mi2 = min( min(self.chan0), min(self.chan1), min(self.chan2), 
                       min(self.chan3), min(self.trigger))
        


        if ma2 > self.highest:
            self.highest = ma2
        if mi2 < self.lowest:
            self.lowest = mi2
        
        self.logger.debug("Chan0 to plot: %s", self.chan0.__repr__())
        
        ma = max( max(self.chan0), max(self.chan1), max(self.chan2),max(self.chan3), max(self.trigger)  )
            
        self.ax.set_ylim(0, ma*1.1)
        
        self.ax.set_xlim(self.l_time[0], self.l_time[-1])

        now2 = datetime.now()
        dt = (now2 - self.now)  
        dt1 = dt.seconds + dt.days * 3600 * 24
        

        string1 = 'started: %s ' % self.now.strftime('%d.%m.%Y %H:%M:%S')

        # we rather calculate the mean rate by dividing
        # total scalars by total time
        try:
            string2 = 'channel0 = %.4e Hz \nchannel1 = %.4e Hz \nchannel2 = %.4e Hz \nchannel3 = %.4e Hz \ntrigger = %.4e Hz' % ( (self.N0)/self.time_window, (self.N1)/self.time_window , (self.N2)/self.time_window, (self.N3)/self.time_window, (self.NT)/self.time_window )
            if self.do_not_show_trigger:
                string2 = 'channel0 = %.4e Hz \nchannel1 = %.4e Hz \nchannel2 = %.4e Hz \nchannel3 = %.4e Hz' % ( (self.N0)/self.time_window, (self.N1)/self.time_window , (self.N2)/self.time_window, (self.N3)/self.time_window )

        except ZeroDivisionError:
            self.logger.debug('Time was Zero!Passing..')
            string2 = ''
            pass

        string3 = 'N0 = %.8e \nN1 = %.8e \nN2 = %.8e \nN3 = %.8e \nNT = %.8e' % (self.N0, self.N1, self.N2, self.N3, self.NT)
        if self.do_not_show_trigger:
            string3 = 'N0 = %.8e \nN1 = %.8e \nN2 = %.8e \nN3 = %.8e' % (self.N0, self.N1, self.N2 , self.N3)

	    # reduce information for better overview
        string4 = '\ndaq time = %.8e s \nmax rate = %.4e Hz' % (  self.time_window, ma2 )
                             
        self.ax.text(1.1, -0.1, string1+string4, transform=self.ax.transAxes) 
        self.ax.text(1.1, 0.35, string3, transform=self.ax.transAxes, color='blue') 
        self.ax.text(1.1, 0.75, string2, transform=self.ax.transAxes, color='green') 
                   
        self.fig.canvas.draw()
        

