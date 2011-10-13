import matplotlib.pyplot as mp
import sys
import pylab as p
import numpy as n


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


class LifetimeMonitor(FigureCanvas):
    """
    A simple histogram for the use with mu lifetime
    measurement
    """
    
    
    def __init__(self,parent,logger):
       
        self.logger = logger
        self.logger.debug("Lifetimemonitor started")

        # first image setup
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)


        # set specific limits for X and Y axes
        #self.ax.set_xlim(0, 1)
        self.ax.set_ylim(ymin=0)
        #self.ax.grid()
        #self.ax.set_title('Lifetime measurement')
        self.ax.set_xlabel('time between pulses (microsec)')
        self.ax.set_ylabel('events')
        # and disable figure-wide autoscale
        #self.ax.set_autoscale_on(False)
        #self.ax.set_autoscale_on(True)
        # generates first "empty" plots

        # make a fixed binning from 0 to 20 microseconds
        # we choose a 0.5 ns binning
        #self.binning = n.linspace(0,20,21)
        self.binning = n.linspace(0,20,84)
        self.bincontent   = self.ax.hist([], self.binning, fc='b', alpha=0.25)[0]
        self.hist_patches = self.ax.hist([], self.binning, fc='b', alpha=0.25)[2]
         
        # force a redraw of the Figure
        self.fig.canvas.draw()
 
        self.setParent(parent)

    def update_plot(self, decaytimes):
        """
        decaytimes must be a list of the last decays
        """

        # avoid memory leak
        self.ax.clear()

        # we have to do some bad hacking here,
        # because the pylab histogram is rather
        # simple and it is not possible to add
        # two of them...
        # however, since we do not run into a memory leak
        # and we also be not dependent on dashi (but maybe
        # sometimes in the future?) we have to do it
        # by manipulating rectangles...

        # we want to find the non-empty bins
        # tmphist is compatible with the decaytime hist...


        print decaytimes
        print decaytimes[0]
        tmphist = self.ax.hist(decaytimes, self.binning, fc='b', alpha=0.25)[0]
        print tmphist

        for histbin in enumerate(tmphist):
            if histbin[1]:
                #self.hist_patches[histbin[0]].set_height(self.hist_patches[histbin[0]].get_height() + histbin[1])
                self.hist_patches[histbin[0]].set_height(self.hist_patches[histbin[0]].get_height() + histbin[1])
                print self.hist_patches[histbin[0]].get_height()
                print self.hist_patches[histbin[0]].set_height(self.hist_patches[histbin[0]].get_height() + histbin[1])
                print self.hist_patches
            else:
                pass

        # we want to get the maximum for the ylims
        heights = []
        for patch in self.hist_patches:
            heights.append(patch.get_height())

        self.ax.set_ylim(ymax=max(heights)*1.1)
        self.ax.set_ylim(ymin=0)
        self.ax.set_xlabel('time between pulses (microsec)')
        self.ax.set_ylabel('events')
        
        # always get rid of unused stuff
        del heights
        del tmphist
 
        # we now have to pass our new patches 
        # to the figure we created..            
        self.ax.patches = self.hist_patches        
        self.fig.canvas.draw()


    
