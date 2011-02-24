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
# used to obtain CPU usage information

##import psutil as p

# Total number of iterations
MAXITERS = 300

class ScalarsMonitor(FigureCanvas):
    """Matplotlib Figure widget to display CPU utilization"""
    def __init__(self,parent,inqueue,outqueue):

        self.inqueue = inqueue
        self.outqueue = outqueue

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
        self.chan0, self.chan1, self.chan2, self.chan3 =[], [], [], []
        self.l_chan0, = self.ax.plot([],self.chan0, label='chan0',lw=3)
        self.l_chan1, = self.ax.plot([],self.chan1, label='chan1',lw=3)
        self.l_chan2, = self.ax.plot([],self.chan2, label='chan2',lw=3)
        self.l_chan3, = self.ax.plot([],self.chan3, label='chan3',lw=3)
        # add legend to plot
        self.ax.legend()
        # force a redraw of the Figure
        self.fig.canvas.draw()
        # initialize the iteration counter
        self.cnt = 0
        # call the update method (to speed-up visualization)
        self.timerEvent(None)
        
        # start timer, trigger event every 1000 millisecs (=1sec)
        self.timer = self.startTimer(5000)

        self.setParent(parent)
        

    def get_scalars(self):
        """Get Scalars"""

        self.outqueue.put('DS')
        #self.outqueue.task_done()
        if not self.inqueue.qsize():
            return (0,0,0,0)
        while self.inqueue.qsize():
             msg = self.inqueue.get(0)
             #self.inqueue.task_done()
             self.scalars = ''
             #print msg
             if msg[0]=='D' and msg[1] == 'S':
                 if len(msg) > 5:
                     self.scalars = msg
                     self.scalars = self.scalars.split()
                     self.scalars_ch0 = int(self.scalars[1][3:],16)
                     self.scalars_ch1 = int(self.scalars[2][3:],16)
                     self.scalars_ch2 = int(self.scalars[3][3:],16)
                     self.scalars_ch3 = int(self.scalars[4][3:],16)
                     self.scalars_trigger = int(self.scalars[5][3:],16)
                     self.scalars_time = int(self.scalars[6][3:],16)               
                     return (self.scalars_ch0/self.scalars_time,self.scalars_ch1/self.scalars_time,self.scalars_ch2/self.scalars_time,self.scalars_ch3/self.scalars_time,self.scalars_trigger/self.scalars_time,self.scalars_time)
                 else:
                     return (0,0,0,0)
             #else:
                 #return (0,0,0,0)
        
            #print 'inqueue empty'
            #self.outqueue.put('CE')
            #self.outqueue.task_done()
            #return (0,0,0,0)
        #self.outqueue.put('CE')
        # Check contents of message and do what it says
        # As a test, we simply print it
        # check for scalar information
        

    def timerEvent(self,ev):
        """Custom timerEvent code, called at timer event receive"""
        # get the cpu percentage usage
        result = self.get_scalars()
        # append new data to the datasets
        self.chan0.append(result[0])
        self.chan1.append(result[1])
        self.chan2.append( result[2])
        self.chan3.append(result[3])
        # update lines data using the lists with new data
        self.l_chan0.set_data(range(len(self.chan0)), self.chan0)
        self.l_chan1.set_data(range(len(self.chan1)), self.chan1)
        self.l_chan2.set_data( range(len(self.chan2)), self.chan2)
        self.l_chan3.set_data(range(len(self.chan3)), self.chan3)
        # force a redraw of the Figure
        self.fig.canvas.draw()
        # if we've done all the iterations
        if self.cnt == MAXITERS:
            # stop the timer
            self.killTimer(self.timer)
        else:
            # else, we increment the counter
            self.cnt += 1

class ScalarsWindow(QtGui.QMainWindow):
    """Example main window"""
    def __init__(self,inque,outque):
        # initialization of Qt MainWindow widget
        QtGui.QMainWindow.__init__(self)
        # set window title
        self.setWindowTitle("Scalars")
        self.inque = inque
        self.outque = outque
        # instantiate a widget, it will be the main one
        self.main_widget = QtGui.QWidget(self)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        qmc = ScalarsMonitor(self.main_widget,self.inque,self.outque)
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(qmc, self.main_widget)
        # pack these widget into the vertical box
        vbl.addWidget(qmc)
        vbl.addWidget(ntb)
        # set the focus on the main widget
        self.main_widget.setFocus()
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)
       
# create the GUI application
#app = QtGui.QApplication(sys.argv)


#sw = ScalarsWindow()
#sw.show()
# Create our Matplotlib widget
#widget = CPUMonitor()
# set the window title
#widget.setWindowTitle("30 Seconds of CPU Usage Updated in RealTime")
# show the widget
#widget.show()
# start the Qt main loop execution, exiting from this script
# with the same return code of Qt application
#sys.exit(app.exec_()) 
