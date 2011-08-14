# for command-line arguments

import matplotlib.pyplot as mp
import sys
import pylab as p

# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui
# Matplotlib Figure object
from matplotlib.figure import Figure
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas
# import the NavigationToolbar Qt4Agg widget
from matplotlib.backends.backend_qt4agg \
import NavigationToolbar2QTAgg as NavigationToolbar


MAXITERS = 300

class LifetimeMonitor(FigureCanvas):
    """histogram of lifetime in coincidence measuring
    To do: * implement coincidence measurement
           * ...  
    """
    
    
    def __init__(self,parent,logger):
       
        # Total number of iterations

        self.MAXITERS = 300
        self.logger = logger
        self.logger.info("Lifetimemonitor started")


        # first image setup
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set specific limits for X and Y axes
        #self.ax.set_xlim(0, 1)
        #self.ax.set_ylim(0, 1)
        #self.ax.grid()
        #self.ax.set_title('Lifetime measurement')
        #self.ax.set_xlabel('lifetime in s')
        #self.ax.set_ylabel('event number')
        # and disable figure-wide autoscale
        #self.ax.set_autoscale_on(False)
        #self.ax.set_autoscale_on(True)
        # generates first "empty" plots
        self.lifetime = [100, 105]
        #print "nachher = ", self.lifetime
        self.lifetime_plot = self.ax.hist(self.lifetime, 20, facecolor='blue', alpha=0.25)
        #mp.show()
        # force a redraw of the Figure
        self.fig.canvas.draw()
        # initialize the iteration counter
        self.cnt = 0
        self.setParent(parent)

    def update_plot(self, lifetime_list):
        self.ax.clear()
        self.lifetime_plot = self.ax.hist(lifetime_list, 20, facecolor='blue', alpha=0.25)       
        self.fig.canvas.draw()

        
        


