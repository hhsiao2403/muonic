# for command-line arguments
import sys
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

class ScalarsMonitor(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self,parent):
       
        # Total number of iterations

        self.MAXITERS = 300

        # first image setup
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set specific limits for X and Y axes
        self.ax.set_xlim(0, 30)
        self.ax.set_ylim(-5, 100)
        self.ax.grid()
        # and disable figure-wide autoscale
        self.ax.set_autoscale_on(False)
        # generates first "empty" plots
        self.chan0, self.chan1, self.chan2, self.chan3, self.trigger =[], [], [], [], []
        self.l_chan0, = self.ax.plot([],self.chan0, label='chan0',lw=3)
        self.l_chan1, = self.ax.plot([],self.chan1, label='chan1',lw=3)
        self.l_chan2, = self.ax.plot([],self.chan2, label='chan2',lw=3)
        self.l_chan3, = self.ax.plot([],self.chan3, label='chan3',lw=3)
        self.l_trigger, = self.ax.plot([],self.chan3, label='trigger',lw=3)
        # add legend to plot
        self.ax.legend()
        # force a redraw of the Figure
        self.fig.canvas.draw()
        # initialize the iteration counter
        self.cnt = 0

        self.setParent(parent)
        


