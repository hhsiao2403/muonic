# This file is part of muonic, a program to work with the QuarkDAQ cards
# Copyright (C) 2009  Robert Franke (robert.franke@desy.de)
#
# muonic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# muonic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with muonic. If not, see <http://www.gnu.org/licenses/>.


# The way of the communication between the serial port and the GUI is based on
# the receipt presented at http://code.activestate.com/recipes/82965/
# Created by Jacob Hallen, AB Strakt, Sweden. 2001-10-17
# Adapted by Boudewijn Rempt, Netherlands. 2002-04-15
# It is licenced under the Python licence, http://www.python.org/psf/license/



class ThreadedClient():
    """
    Launch the main part of the GUI and the worker threads. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, opts,logger,root):

        global MULTICORE

        # Create the queue
        if MULTICORE:
            # mult.Queue or mult.JoinableQueue?
            # self.outqueue = mult.JoinableQueue()
            # self.inqueue  = mult.JoinableQueue()
            self.outqueue = mult.Queue()
            self.inqueue  = mult.Queue()
            
        else:    
            self.outqueue = Queue.Queue()
            self.inqueue = Queue.Queue()

        self.running = 1
        self.root = root

        # get option parser options
        self.logger = logger
        self.sim = opts.sim
        self.filename = opts.filename
        self.timewindow = float(opts.timewindow)
        self.inputfile = opts.inputfile

        # Set up the GUI part
        self.gui=MainWindow(self.outqueue, self.inqueue, self.endApplication, self.filename, self.logger, self.timewindow) 
        self.gui.show()

        # A timer to periodically call periodicCall :-)
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,
                           QtCore.SIGNAL("timeout()"),
                           self.periodicCall)

        # Start the timer -- this replaces the initial call to periodicCall
        self.timer.start(1000)

        if self.sim:
            self.daq = SimDaqConnection(self.inqueue, self.outqueue, self.logger)
        elif self.inputfile:
            self.daq = FileDaqConnection(self.inqueue, self.outqueue,self.inputfile, self.logger)
            # we have to use the timestamp from the file
            self.gui.options.usecpld = True

        else:
            self.daq = DaqConnection(self.inqueue, self.outqueue, self.logger)
        
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        if MULTICORE:
            self.readthread = mult.Process(target=self.daq.read,name="pREADER")
            if not self.sim:
                if not self.inputfile:
                    self.writethread = mult.Process(target=self.daq.write,name="pWRITER")
        else:
            self.readthread = threading.Thread(target=self.daq.read)
            if not self.sim:
                self.writethread = threading.Thread(target=self.daq.write)
                if not self.inputfile:
                    self.writethread = threading.Thread(target=self.daq.write)
        
        # Set daemon flag so that the threads finish when the main app finishes
        self.readthread.daemon = True
        self.readthread.start()
        if not self.sim:
            if not self.inputfile:
                self.writethread.daemon = True
                self.writethread.start()
        

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            self.daq.running = False
	    self.mu_file.close()
            self.root.quit()

    def endApplication(self):
        self.running = False
 
def main(opts,logger):
    root = QtGui.QApplication(sys.argv)
    client = ThreadedClient(opts,logger,root)
    root.exec_()

if __name__ == '__main__':

    import sys
    import os
    from optparse import OptionParser



    usage = "%prog [options] -f <data output file> \nspecify the file type by a command line switch."
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", dest="filename", help="write data to FILE", metavar="FILE", default=None)
    #parser.add_option("-d", "--debug", action="store_true", dest="debug", help="output for debugging", default=False)
    parser.add_option("-s", "--sim", action="store_true", dest="sim", help="use simulation mode for testing without hardware", default=False)
    parser.add_option("-t", "--timewindow", dest="timewindow", help="time window for the measurement in s (default 5 s)", default=5.0)
    parser.add_option("-d", "--debug", dest="loglevel", action="store_const", const=10 , help="switch to loglevel debug", default=20)
    parser.add_option("-i", "--inputfile", dest="inputfile", help="read data from FILE instead from DAQ card", metavar="INFILE", default=None)
    opts, args = parser.parse_args()

    if opts.filename is None:
        print "No filename for saving the data was entered, please use e.g. \ndaq.py -f data.txt \nor call daq.py -h or daq.py --help for help"
    if os.path.exists(opts.filename):
        decision = raw_input("A file with the filename %s already exists. Do you really want to overwrite it (yes/no)? " % str(opts.filename) )

        if decision != 'yes':
            print "Program is terminated because a file with the filename %s aready exits and you have chosen that it should not be overwritten. Please restart the program and choose another filename" % opts.filename
            sys.exit()

    import logging

    logger = logging.getLogger()
    logger.setLevel(int(opts.loglevel))
    ch = logging.StreamHandler()
    ch.setLevel(int(opts.loglevel))
    formatter = logging.Formatter('%(levelname)s:%(process)d:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    #even if multiprocessing.Queue is used, Queue is needed 
    import Queue
   

    #test if more than one cpu is available
    try:
        import multiprocessing as mult
        MULTICORE = mult.cpu_count() > 1
        logger.info("%d cpus found!" %mult.cpu_count())
   
    except ImportError:
        logger.info("python-multiprocessing is not available, using python thrading instead")
        MULTICORE = False


    if not MULTICORE: 
        import threading
    else:
        logger.info("using python-multiprocessing expansion")
    
    
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    
    from daq.DaqConnection import DaqConnection
    from daq.SimDaqConnection import SimDaqConnection
    from daq.FileDaqConnection import FileDaqConnection
    from gui.MainWindow import MainWindow

    # make it so!
    main(opts,logger)

# vim: ai ts=4 sts=4 et sw=4
